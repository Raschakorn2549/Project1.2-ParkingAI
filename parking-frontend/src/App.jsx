import { useState, useEffect, useCallback } from 'react'

// ====== Stat Card ======
function StatCard({ label, value, color, icon }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 flex flex-col gap-2">
      <div className="flex items-center gap-2 text-gray-500 text-xs uppercase tracking-widest">
        <span>{icon}</span>
        <span>{label}</span>
      </div>
      <div className={`text-5xl font-bold ${color}`}>{value}</div>
      <div className="text-gray-600 text-xs">ช่องจอด</div>
    </div>
  )
}

// ====== Toast ======
function Toast({ message, show }) {
  return (
    <div className={`
      fixed bottom-6 right-6 bg-gray-900 border border-gray-700
      rounded-xl px-5 py-3 text-sm text-green-400
      transition-all duration-300 pointer-events-none
      ${show ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2'}
    `}>
      {message}
    </div>
  )
}

// ====== Main App ======
export default function App() {
  const [data, setData]           = useState({ Occupancy: 0, Available: 0 })
  const [lastUpdate, setLastUpdate] = useState('—')
  const [sending, setSending]     = useState(false)
  const [toast, setToast]         = useState({ show: false, message: '' })

  // ดึงข้อมูลทุก 1 วินาที
  useEffect(() => {
    const fetch_data = () => {
      fetch('/data')
        .then(r => r.json())
        .then(d => {
          setData(d)
          setLastUpdate(new Date().toLocaleTimeString('th-TH'))
        })
        .catch(() => {})
    }
    fetch_data()
    const id = setInterval(fetch_data, 1000)
    return () => clearInterval(id)
  }, [])

  const total = data.Occupancy + data.Available
  const pct   = total > 0 ? Math.round((data.Occupancy / total) * 100) : 0

  // progress bar color
  const barColor =
    pct >= 90 ? 'bg-red-500' :
    pct >= 60 ? 'bg-yellow-500' :
    'bg-green-500'

  // ส่ง LINE
  const sendLine = useCallback(() => {
    setSending(true)
    fetch('/send_line', { method: 'POST' })
      .then(r => r.json())
      .then(() => showToast('✅ ส่ง LINE สำเร็จแล้ว!'))
      .catch(() => showToast('❌ ส่ง LINE ไม่สำเร็จ'))
      .finally(() => setTimeout(() => setSending(false), 2000))
  }, [])

  const showToast = (msg) => {
    setToast({ show: true, message: msg })
    setTimeout(() => setToast({ show: false, message: '' }), 3000)
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white">

      {/* Header */}
      <header className="bg-gray-900 border-b border-gray-800 px-8 py-4 flex items-center gap-3">
        <h1 className="text-xl font-medium flex-1">🅿️ Parking Dashboard</h1>
        <span className="bg-red-600 text-white text-xs font-semibold px-3 py-1 rounded-full animate-pulse">
          ● LIVE
        </span>
      </header>

      <main className="p-8 flex flex-col gap-6 max-w-5xl mx-auto">

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4">
          <StatCard label="ถูกใช้งาน" value={data.Occupancy} color="text-red-400"   icon="🚗" />
          <StatCard label="ว่าง"      value={data.Available}  color="text-green-400" icon="✅" />
          <StatCard label="ทั้งหมด"   value={total}           color="text-blue-400"  icon="🅿️" />
        </div>

        {/* Progress bar */}
        <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6">
          <div className="flex justify-between text-sm text-gray-400 mb-3">
            <span>อัตราการใช้งาน</span>
            <span className="font-medium text-white">{pct}%</span>
          </div>
          <div className="bg-gray-800 rounded-full h-3 overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-500 ${barColor}`}
              style={{ width: `${pct}%` }}
            />
          </div>
          <div className="flex justify-between text-xs text-gray-600 mt-2">
            <span>ว่าง</span>
            <span>เต็ม</span>
          </div>
        </div>

        {/* Video */}
        <div className="bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden">
          <div className="px-5 py-4 border-b border-gray-800 text-sm text-gray-400 flex items-center gap-2">
            <span>📷</span>
            <span>กล้องวงจรปิด — Real-time</span>
          </div>
          <img
            src="/video_feed"
            alt="Parking Camera"
            className="w-full block"
          />
        </div>

        {/* LINE Button */}
        <button
          onClick={sendLine}
          disabled={sending}
          className={`
            w-full flex items-center justify-center gap-3
            rounded-2xl py-4 text-base font-semibold
            transition-all duration-200
            ${sending
              ? 'bg-gray-800 text-gray-500 cursor-not-allowed'
              : 'bg-green-500 hover:bg-green-400 active:scale-95 text-white'}
          `}
        >
          <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
            <path d="M12 2C6.48 2 2 6.03 2 11c0 3.13 1.73 5.88 4.34 7.54L5.5 22l3.72-1.96C10.04 20.65 11 20.8 12 20.8c5.52 0 10-4.03 10-9s-4.48-9-10-9z"/>
          </svg>
          {sending ? 'กำลังส่ง...' : 'ส่งสถานะไปยัง LINE'}
        </button>

        {/* Status bar */}
        <div className="bg-gray-900 border border-gray-800 rounded-2xl px-5 py-4 flex items-center gap-3 text-sm text-gray-500">
          <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          <span>ระบบทำงานปกติ</span>
          <span className="ml-auto">อัปเดตล่าสุด: {lastUpdate}</span>
        </div>

      </main>

      <Toast message={toast.message} show={toast.show} />
    </div>
  )
}