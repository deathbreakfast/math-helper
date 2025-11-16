import { motion, type HTMLMotionProps } from 'framer-motion'

type AnimationProps = Omit<HTMLMotionProps<'div'>, 'initial' | 'animate'>

export const FadeIn = ({ children, className = '', ...props }: AnimationProps) => (
  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className={className} {...props}>
    {children}
  </motion.div>
)

export const SlideUp = ({ children, className = '', ...props }: AnimationProps) => (
  <motion.div
    initial={{ opacity: 0, y: 16 }}
    animate={{ opacity: 1, y: 0 }}
    className={className}
    {...props}
  >
    {children}
  </motion.div>
)

export const SlideDown = ({ children, className = '', ...props }: AnimationProps) => (
  <motion.div
    initial={{ opacity: 0, y: -16 }}
    animate={{ opacity: 1, y: 0 }}
    className={className}
    {...props}
  >
    {children}
  </motion.div>
)

export const ScaleIn = ({ children, className = '', ...props }: AnimationProps) => (
  <motion.div
    initial={{ opacity: 0, scale: 0.95 }}
    animate={{ opacity: 1, scale: 1 }}
    className={className}
    {...props}
  >
    {children}
  </motion.div>
)

