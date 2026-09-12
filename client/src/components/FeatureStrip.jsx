import { FileText, ShieldCheck, Lock } from 'lucide-react';

const FEATURES = [
  {
    icon: <FileText size={28} className="text-blue-400" />,
    title: 'Paste Anywhere',
    desc: 'Works with LinkedIn, Handshake, emails, or any job board.',
  },
  {
    icon: <ShieldCheck size={28} className="text-green-400" />,
    title: 'Spot Hidden Scams',
    desc: 'We flag pay-to-join schemes, vague roles, and fake companies.',
  },
  {
    icon: <Lock size={28} className="text-slate-400" />,
    title: 'Protect Your Info',
    desc: 'Never share personal or bank details without verifying first.',
  },
];

export default function FeatureStrip() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-8 max-w-3xl mx-auto mt-16 pb-16 px-4">
      {FEATURES.map((f, i) => (
        <div
          key={i}
          className="flex flex-col items-center text-center gap-3"
        >
          <div
            className="w-14 h-14 rounded-2xl flex items-center justify-center"
            style={{
              background: 'rgba(15,32,64,0.7)',
              border: '1px solid rgba(59,130,246,0.15)',
            }}
          >
            {f.icon}
          </div>
          <h4 className="font-semibold text-white text-sm">{f.title}</h4>
          <p className="text-xs text-slate-500 leading-relaxed">{f.desc}</p>
        </div>
      ))}
    </div>
  );
}
