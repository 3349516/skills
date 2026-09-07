# 事件处理完整规范（摘自官方 UI events 指南）

## 决策树（官方原图的逻辑）

```
事件从哪来？─┬─ 从 ViewModel 来 ──────────→ 转成 UiState 更新（绝不让 VM 直接调 UI）
            ├─ 从 UI 来，需要业务逻辑   → 委托给 ViewModel 暴露的函数（动词命名）
            └─ 从 UI 来，纯 UI 行为逻辑 → 直接在 UI 里改状态（如菜单展开收起）
```

判断"UI 逻辑 vs 业务逻辑"：导航决策、展示消息、可展开状态 = UI 逻辑；支付、请求刷新、持久化偏好 = 业务逻辑。

## 模式一：一次性消息（userMessage 模式）——官方标准

ViewModel 事件永远表现为状态更新，保证配置变更后消息不丢、可复现。

```kotlin
// ViewModel
data class NewsUiState(val userMessage: String? = null)

private val _userMessage = MutableStateFlow<String?>(null)
fun userMessageShown() { _userMessage.value = null }   // 消费完毕回调

// UI（Compose）
@Composable
fun NewsScreen(uiState: NewsUiState, onMessageShown: () -> Unit) {
    val snackbarHostState = remember { SnackbarHostState() }

    uiState.userMessage?.let { message ->
        LaunchedEffect(snackbarHostState, message) {
            snackbarHostState.showSnackbar(message)
            onMessageShown()        // 展示完通知 VM 清空状态
        }
    }
}
```

## 模式二：导航事件 —— 状态化 + 生命周期感知收集

不要把"去登录页"做成一次性事件流；把**导航的依据**（如 `isUserLoggedIn`）放进 UiState，UI 观察状态变化后自行导航。

```kotlin
val lifecycle = LocalLifecycleOwner.current.lifecycle
val currentOnUserLogIn by rememberUpdatedState(onUserLogIn)   // 总是最新 lambda

LaunchedEffect(viewModel, lifecycle) {
    snapshotFlow { viewModel.uiState.value }        // State → Flow
        .filter { it.isUserLoggedIn }               // 只关心目标状态
        .flowWithLifecycle(lifecycle)               // 至少 STARTED 才收集
        .collect { currentOnUserLogIn() }
}
```

## 模式三：返回栈保留场景（A→B 后还能返回 A）

问题：配置变更/返回重放会触发重复导航。官方方案：**导航意图状态放 UI 侧**（`rememberSaveable`），因为导航属于 UI 逻辑不是 VM 职责；VM 只负责校验并产出结果状态。

```kotlin
// VM 只产出校验结果状态
data class RegistrationUiState(val isDobValid: Boolean = false)

// UI 持有导航意图，避免重放
var validationInProgress by rememberSaveable { mutableStateOf(false) }

Button(onClick = {
    validationInProgress = true
    viewModel.validateInput()       // 上报业务事件
}) { Text("Register") }

LaunchedEffect(validationInProgress, uiState.isDobValid) {
    if (validationInProgress && uiState.isDobValid) {
        validationInProgress = false
        navController.popBackStack()   // 或 navigate(...)
    }
}
```

## 模式四：列表项事件 —— lambda 随状态下发

把每个列表项要触发的事件以 lambda 存进 item 的 UiState，列表 UI 只调用、不感知 VM。这样整个列表组件完全无状态、可复用（官方 Views 版用 RecyclerView 适配器同理）。

```kotlin
data class NewsItemUiState(
    val title: String,
    val bookmarked: Boolean = false,
    val onBookmark: () -> Unit,     // VM 构造状态时注入 ::addBookmark
)
```

## 反模式（禁止）

- ❌ VM 持有 `NavController` / SnackbarHost / Context 去直接执行 UI 动作；
- ❌ 用 SharedFlow"事件总线"让 VM 向 UI 发一次性指令（官方明确不推荐，丢失状态、无法复现）；
- ❌ 在无状态内容函数里 import 或转发 ViewModel；
- ❌ 用户输入每次 onChange 都启动协程做校验——校验结果本身做成状态。
