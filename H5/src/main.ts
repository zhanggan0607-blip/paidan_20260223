import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './style.css'

import {
  NavBar,
  Cell,
  CellGroup,
  Grid,
  GridItem,
  Badge,
  Icon,
  Button,
  Field,
  Popup,
  Picker,
  DatePicker,
  Calendar,
  Tabs,
  Tab,
  List,
  PullRefresh,
  Tag,
  Empty,
  ActionSheet,
  Popover,
  ImagePreview,
  Loading,
  NoticeBar,
} from 'vant'
import 'vant/lib/index.css'

const app = createApp(App)

app.use(NavBar)
app.use(Cell)
app.use(CellGroup)
app.use(Grid)
app.use(GridItem)
app.use(Badge)
app.use(Icon)
app.use(Button)
app.use(Field)
app.use(Popup)
app.use(Picker)
app.use(DatePicker)
app.use(Calendar)
app.use(Tabs)
app.use(Tab)
app.use(List)
app.use(PullRefresh)
app.use(Tag)
app.use(Empty)
app.use(ActionSheet)
app.use(Popover)
app.use(ImagePreview)
app.use(Loading)
app.use(NoticeBar)

app.use(router)
app.mount('#app')
