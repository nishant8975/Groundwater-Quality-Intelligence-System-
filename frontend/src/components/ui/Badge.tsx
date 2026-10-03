import { clsx } from 'clsx';
import { WawqiCategory } from '../../types';

export function CategoryBadge({ category }: { category: WawqiCategory | string }) {
  const styles = {
    'Excellent': 'bg-wawqi-excellent/10 text-wawqi-excellent border-wawqi-excellent/20',
    'Good': 'bg-wawqi-good/10 text-wawqi-good border-wawqi-good/20',
    'Poor': 'bg-wawqi-poor/10 text-wawqi-poor border-wawqi-poor/20',
    'Very Poor': 'bg-wawqi-very_poor/10 text-wawqi-very_poor border-wawqi-very_poor/20',
    'Unsuitable': 'bg-wawqi-unsuitable/10 text-wawqi-unsuitable border-wawqi-unsuitable/20',
    'UNAVAILABLE': 'bg-wawqi-unavailable/10 text-wawqi-unavailable border-wawqi-unavailable/20',
  };
  
  const defaultStyle = 'bg-slate-800 text-slate-300 border-slate-700';
  const appliedStyle = styles[category as keyof typeof styles] || defaultStyle;

  return (
    <span className={clsx("inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border", appliedStyle)}>
      {category}
    </span>
  );
}
