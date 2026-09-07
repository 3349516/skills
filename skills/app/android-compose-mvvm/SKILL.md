---
name: android-compose-mvvm
description: Android Jetpack Compose 的 MVVM / UI 层架构规范（Android 官方指南口径）：UiState 建模、ViewModel 封装、状态提升、单向数据流(UDF)、事件与导航处理、屏幕四件套模板。凡是新建或重构 Compose 页面、编写 ViewModel/UiState、讨论状态管理与界面刷新、事件上抛、MVVM 或 UI 架构分层时使用本 skill——用户没有明说 MVVM 也要用。
---

# Android Compose MVVM / UI 架构规范

本规范来自 Android 官方文档（UI layer / UI events / Compose architecture），适用于任何 app。产出代码时严格按此执行；回答架构问题时以此为准。

先判断任务类型，再动手：

- **新建页面** → 直接按「四件套模板」产出代码；
- **重构现有页面** → 先执行「重构流程」，再产出代码；
- **只问架构问题** → 用本规范回答，按需读 references/。

## 核心铁律（单向数据流 UDF）

1. **状态向下流动**：ViewModel 生产不可变 UiState，UI 只读渲染；
2. **事件向上流动**：UI 调用 ViewModel 暴露的函数上报，VM 改状态驱动界面；
3. ViewModel 发起的一切界面动作（Toast / Snackbar / 导航）**必须建模为 UiState 的一部分**，禁止 VM 持有或直接调用 UI；
4. UiState 必须不可变（data class + val + 默认值）；一个屏幕一个 UiState、一个 ViewModel；
5. ViewModel 构造函数只依赖数据层（Repository / UseCase），禁止持有 Context、View 或 Composable 引用。

## 屏幕四件套模板（新建页面照抄此结构）

```kotlin
/* ── 1. UiState：不可变的屏幕快照，命名约定「功能名 + UiState」────────── */

data class NewsUiState(
    val loading: Boolean = false,
    val newsItems: List<NewsItemUiState> = emptyList(),
    val userMessage: String? = null,      // 一次性消息(Snackbar/Toast)也建模为状态
)

data class NewsItemUiState(
    val title: String,
    val bookmarked: Boolean = false,
    val onBookmark: () -> Unit,           // 列表项事件：以 lambda 随状态下发
)

/* ── 2. ViewModel：唯一状态生产者 ────────────────────────────────────── */

class NewsViewModel(
    private val newsRepository: NewsRepository,
    savedStateHandle: SavedStateHandle,   // 需要导航参数/进程恢复时再加
) : ViewModel() {

    private val _userMessage = MutableStateFlow<String?>(null)

    val uiState: StateFlow<NewsUiState> = combine(
        newsRepository.latestNews,
        _userMessage,
    ) { news, msg ->
        NewsUiState(
            loading = false,
            newsItems = news.toUiItems(),
            userMessage = msg,
        )
    }.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5_000),
        initialValue = NewsUiState(loading = true),
    )

    /** 事件处理函数：动词命名；viewmodelScope + 挂起调用，保持 main-safe */
    fun addBookmark(id: String) {
        viewModelScope.launch { newsRepository.addBookmark(id) }
    }

    /** 一次性消息消费完毕的回调（UI 展示后调用，状态清空） */
    fun userMessageShown() { _userMessage.value = null }
}

/* ── 3. 有状态入口 Composable：拿 VM → 转状态 → 转发事件 ──────────────── */

@Composable
fun NewsScreen(
    onNavigateToArticle: (String) -> Unit,   // 导航 lambda 由调用方传入
    viewModel: NewsViewModel = viewModel(),
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    NewsScreen(                              // 委托给同名无状态版本
        uiState = uiState,
        onBookmark = viewModel::addBookmark,
        onMessageShown = viewModel::userMessageShown,
        onNavigateToArticle = onNavigateToArticle,
    )
}

/* ── 4. 无状态内容 Composable：只收 state + lambda ───────────────────── */

@Composable
fun NewsScreen(
    uiState: NewsUiState,
    onBookmark: (String) -> Unit,
    onMessageShown: () -> Unit,
    onNavigateToArticle: (String) -> Unit,
) {
    // 渲染 uiState；不 import 任何 ViewModel —— 因此可直接 @Preview、可单独测试
}
```

同名两个函数（有状态入口 + 无状态内容）是官方标准拆分，不要合成一个。

## 有状态 vs 无状态（判断标准）

- **无状态（stateless）**：自己不持有任何状态，所需数据与事件全部经参数传入（`value` + `onValueChange` 模式）。收益：可复用、可单测、可直接 `@Preview` 传假数据。
- **有状态（stateful）**：拥有状态的生产与持有（函数内 `remember`，或接入 ViewModel）。官方惯用法：**有状态函数拥有状态，并调用无状态函数渲染**——四件套里的入口函数就是有状态侧，内容函数就是无状态侧。
- 判断口诀：函数体内出现 `remember` / `mutableStateOf` / `ViewModel` = 有状态；参数全是 state + lambda = 无状态。
- **状态提升就是把组件从有状态改造成无状态的技术**（把 `remember { mutableStateOf() }` 换成一对参数上抛给调用方）；屏幕级提升到 ViewModel，组件级提升到调用方。
- 自定义可复用组件（输入框、弹窗、卡片、列表项等）**默认设计成无状态**，状态和事件由调用方传入；只有无人共享的纯 UI 状态（如菜单展开收起）才留在组件内部。

## 状态暴露选型

| | `StateFlow` + `stateIn` + `collectAsStateWithLifecycle()`（默认） | `var uiState by mutableStateOf()` + `private set` |
|---|---|---|
| 生命周期感知 | ✅ 退后台自动停收集 | ❌ |
| Flow 操作符 | ✅ map/filter/combine | ❌（配 `snapshotFlow` 可转出） |
| 样板代码 | 稍多 | 最少 |

**默认用 StateFlow 方案**；纯 Compose 小项目可用 mutableStateOf 方案；同一份数据禁止两种方式混用。详细对比见 [references/state-and-logic.md](references/state-and-logic.md)。

## 事件处理决策树（详版见 references/events.md）

```
事件从哪来？─┬─ 从 ViewModel 来 ──────────→ 必须转成 UiState 更新（userMessage 模式）
            ├─ 从 UI 来，需要业务逻辑   → 委托给 VM 的函数（动词命名）
            └─ 从 UI 来，纯 UI 行为逻辑 → 直接在 UI 改本地状态（如 expanded = !expanded）
```

导航事件用「状态 + snapshotFlow + flowWithLifecycle」消费；返回栈保留场景的导航意图状态放 UI 侧（rememberSaveable）。完整代码在 [references/events.md](references/events.md)。

## 逻辑与状态归属速查

| 内容 | 归属 |
|---|---|
| 纯 UI 局部状态（开关、输入草稿） | Composable 内 `remember` / `rememberSaveable` |
| 复杂 UI 逻辑、跨多个子组件 | 普通状态持有类（`@Stable` + `rememberXxxState()` 工厂，如 `LazyListState`） |
| 屏幕级业务逻辑、数据合并 | ViewModel |
| 跨屏共享数据、缓存 | 数据层 Repository（VM 只做中转/合并，不长期持有业务数据） |

状态提升三规则：提升到所有读取者的最低共同父级；提升到可能修改它的最高层级；因同一事件一起变化的状态一起提升。不要过度提升——无人共享的状态留在组件内部。

## 重构流程（改造现有页面时）

1. 通读现有页面，列出：当前状态有哪些、各在哪里被读写、哪些是 UI 逻辑哪些是业务逻辑；
2. 按「四件套」重排文件结构（同包下：`XxxUiState.kt`、`XxxViewModel.kt`、`XxxScreen.kt`，或 UiState 与 VM 同文件）；
3. 把散落的状态收拢进 UiState；把对数据的直接操作改为 VM 事件函数；
4. 把 Toast/Snackbar/导航等"直接调用"改为状态驱动；
5. 跑「自查清单」，全部通过才算完成。

## 自查清单（交付前逐条核对）

- [ ] UiState 不可变：data class、全 val、有默认值、含 loading 与一次性消息字段
- [ ] 一个屏幕一个 ViewModel；VM 无 Context/View 引用，构造只依赖数据层
- [ ] Android 上收集 Flow 一律 `collectAsStateWithLifecycle()`
- [ ] 无状态内容函数不 import ViewModel、参数只有 state + lambda
- [ ] 可复用自定义组件（输入框/弹窗/卡片/列表项）默认无状态，state 与事件由参数传入
- [ ] VM→UI 的动作（消息/导航）全部状态化，无一例外
- [ ] 事件函数动词命名（`addBookmark`、`refreshNews`）
- [ ] main-safe：VM 不手动切 Dispatcher（`Dispatchers.IO` 属于数据层职责）
- [ ] 列表用不可变 List + key；长列表分页考虑 Paging（`LazyPagingItems` 直接暴露给 UI）

## 参考资料（官方）

- UI 层架构：https://developer.android.com/topic/architecture/ui-layer
- UI 事件：https://developer.android.com/topic/architecture/ui-layer/events
- 状态持有者：https://developer.android.com/topic/architecture/ui-layer/stateholders
- Compose 架构：https://developer.android.com/develop/ui/compose/architecture
- 状态提升：https://developer.android.com/develop/ui/compose/state-hoisting
- 旗舰示例：https://github.com/android/nowinandroid （feature 模块三件套：Screen + ViewModel + Navigation）
