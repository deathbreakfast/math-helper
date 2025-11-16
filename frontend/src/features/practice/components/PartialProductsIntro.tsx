import { Notice } from '../../../components/common/Notice'

type PartialProductsIntroProps = {
  operandsLabel: string
}

export const PartialProductsIntro = ({ operandsLabel }: PartialProductsIntroProps) => {
  return (
    <Notice
      variant="info"
      tone="indigo"
      icon="lightbulb"
      body={`Break down ${operandsLabel} into partial products, then add them to show your final answer.`}
    />
  )
}

