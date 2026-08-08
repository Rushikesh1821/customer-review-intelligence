export default function Tabs({ tabs, activeTab, onChange }) {
  return <div className="tabs" role="tablist">{tabs.map((tab) => <button key={tab.id} type="button" role="tab" aria-selected={activeTab === tab.id} className={`tab ${activeTab === tab.id ? 'active' : ''}`} onClick={() => onChange(tab.id)}>{tab.label}</button>)}</div>;
}
