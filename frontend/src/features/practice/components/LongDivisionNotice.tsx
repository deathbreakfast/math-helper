import type { NoticeConfig } from '../types'
import { Notice } from '../../../components/common/Notice'

type LongDivisionNoticeProps = {
  notice: NoticeConfig
}

export const LongDivisionNotice = ({ notice }: LongDivisionNoticeProps) => {
  const variant = notice.tone === 'orange' ? 'warning' : notice.tone === 'emerald' ? 'success' : 'info'
  const icon = notice.icon === 'info' ? 'info' : 'lightbulb'

  return <Notice variant={variant} tone={notice.tone} icon={icon} title={notice.title} body={notice.body} />
}

