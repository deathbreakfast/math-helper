type FilterChipsProps = {
  options: string[]
  value: string
  onChange: (value: string) => void
}

const FilterChips = ({ options, value, onChange }: FilterChipsProps) => (
  <div className="flex gap-2">
    {options.map((option) => (
      <button
        key={option}
        onClick={() => onChange(option)}
        className={`rounded-xl px-3 py-1 text-xs font-semibold capitalize ${
          value === option ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
        }`}
      >
        {option}
      </button>
    ))}
  </div>
)

export default FilterChips

