# 状态暴露、逻辑归属与进阶主题（摘自官方文档）

## 一、状态暴露两种官方写法完整对比

### 方案 A（默认）：StateFlow + stateIn + collectAsStateWithLifecycle

```kotlin
class ConversationViewModel(...) : ViewModel() {
    val uiState: StateFlow<ConversationUiState> =
        conversationSource
            .map { ConversationUiState(it) }
            .stateIn(
                scope = viewModelScope,
                started = SharingStarted.WhileSubscribed(5_000),
                initialValue = ConversationUiState(),
            )
}
// UI: val uiState by viewModel.uiState.collectAsStateWithLifecycle()
```

要点：
- `WhileSubscribed(5_000)`：最后一位订阅者离开 5 秒后停止上游（旋转屏幕不重启流）；
- 需要 `lifecycle-runtime-compose` 依赖；这是 Android 上收集 Flow 的官方推荐方式。

### 方案 B：Compose 状态直放 VM

```kotlin
class ConversationViewModel : ViewModel() {
    var uiState by mutableStateOf(ConversationUiState())
        private set                    // 只读暴露，写只经事件函数

    fun addMessage(msg: String) {
        uiState = uiState.copy(messages = uiState.messages + msg)
    }
}
// UI: 直接读 vm.uiState 即响应式
```

### 选型

| 维度 | A: StateFlow | B: mutableStateOf |
|---|---|---|
| 生命周期感知收集 | ✅ | ❌ |
| 操作符(map/combine/filter) | ✅ | ❌ |
| 供非 Compose 端(View/测试)消费 | ✅ | ❌ |
| 样板代码 | 多 | 最少 |
| 细粒度重组（只更新变化字段） | 需拆多流 | 天然支持 |

默认 A；小体量纯 Compose 应用可 B；**同一份数据禁止 A/B 混用**。VM 内如需把 B 转 Flow 加工：`snapshotFlow { uiState.xxx }`。

## 二、UI State 的构建管线（官方 state production 指南）

状态生产分两层，中间层(VM)只做转换，不做数据持有：

```
数据层(Repository/UseCase)          ViewModel(UI state 生产中间层)          UI
  原始数据、缓存、线程切换    ──→    合并多源、数据→UiState 映射、    ──→   渲染
  (Dispatchers 在这层)              业务事件处理(纯函数优先)
```

- **线性转换**（一对一）：直接 `.map {}`；
- **多源合并**：`combine(flow1, flow2) { a, b -> ... }`；
- **需要先前值**：用 `withMutableStateList {}`、`toMutableStateList()` 这类 SnapshotList API 或 `scan`；
- **纯函数构建**：UiState 的派生逻辑写成无副作用纯函数，便于单测。

## 三、单流 vs 多流

默认**单一 UiState 流**（简单、状态一致）；仅当屏幕不同区域更新频率差异巨大（如输入框 + 列表）时拆多流，拆分后每个流各自 `stateIn`。

## 四、分页（Paging）

不要把分页数据包进 UiState。直接暴露 `Flow<PagingData>`，UI 用：

```kotlin
val pagingItems: Flow<PagingData<NewsItemUiState>> = ...
// UI: val items = viewModel.pagingItems.collectAsLazyPagingItems()
```

其余筛选条件、加载态仍走普通 UiState。

## 五、普通状态持有类（plain state holder）

UI 逻辑复杂但不涉业务时，用组合内状态持有类，跟随组合生命周期：

```kotlin
@Stable
class CallState(currentCall: PhoneCall) {
    var currentCall by mutableStateOf(currentCall)
        private set
    var speakerphoneEnabled by mutableStateOf(false)

    fun toggleSpeakerphone() { ... }
    fun updateCall(call: PhoneCall) { ... }
}

@Composable
fun rememberCallState(call: PhoneCall): CallState = remember(call) { CallState(call) }
```

惯用工厂命名 `rememberXxxState()`（同 `rememberLazyListState()` / `rememberScrollState()`）。

## 六、线程规则

- VM 的所有公开 API 必须 **main-safe**：内部用挂起函数，Dispatcher 切换（`withContext(Dispatchers.IO)`）是**数据层**的职责；
- 禁止 `viewModelScope.launch(Dispatchers.IO) { ... }` 出现在 VM；
- `combine`/`map` 链中不做耗时阻塞操作。

## 七、测试要点

- ViewModel 单测：不需要 Compose 环境；StateFlow 方案用 `first()`/turbo collector 断言；构造 fake Repository 直接传入；
- 无状态内容函数：UI 测试直接传任意假 UiState（这也是四件套拆分的最大红利）；
- 一次性消息：断言"消费回调后状态清空"。

## 八、官方文档索引

- UI 层：https://developer.android.com/topic/architecture/ui-layer
- 事件：https://developer.android.com/topic/architecture/ui-layer/events
- 状态持有者：https://developer.android.com/topic/architecture/ui-layer/stateholders
- 状态生产管线：https://developer.android.com/topic/architecture/ui-layer/state-production
- ViewModel：https://developer.android.com/topic/libraries/architecture/viewmodel
- Compose 架构：https://developer.android.com/develop/ui/compose/architecture
- 状态提升：https://developer.android.com/develop/ui/compose/state-hoisting
- 状态与 Compose：https://developer.android.com/develop/ui/compose/state
- Now in Android（旗舰参考）：https://github.com/android/nowinandroid
