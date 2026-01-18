import React, { useState, useRef, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation, useNavigate } from 'react-router-dom';
import { Sprout, ScanLine, TrendingUp, Activity, Upload, Volume2, BrainCircuit, Settings, Globe, Home, BookOpen, MessageSquare, Zap, Dna, Hexagon, AlertTriangle, RefreshCw, Play, ChevronRight, ArrowUpRight, ArrowRight, CloudRain, Search, ChevronLeft, Droplets, Timer, Target, Mic, Send, BarChart3, ExternalLink, Loader2, DollarSign, Package, Radio } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import axios from 'axios';
import CultivationView from './components/CultivationView'; // Import the new View

// --- Global UI ---
// ... (rest of App.jsx unchanged until KnowledgeCore)

// --- Knowledge Core: Dynamic Botanical Intelligence ---
const KnowledgeCore = () => {
  const [crops, setCrops] = useState([]);
  const [selected, setSelected] = useState(null);
  const [viewMode, setViewMode] = useState('detail'); // 'detail' | 'cultivation'
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    // Fetch crops from backend
    axios.get('http://localhost:5000/api/crops')
      .then(res => {
        setCrops(res.data.crops);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load crops:', err);
        setLoading(false);
      });
  }, []);

  const handleLaunchVani = (crop) => {
    // AI Context Bridge
    const context = `I'm interested in ${crop.name} (${crop.scientific}, variety: ${crop.variety}). ` +
      `This crop has a cycle of ${crop.cycle}, requires ${crop.water} irrigation, ` +
      `and yields ${crop.yield}. It's grown in ${crop.region}. ` +
      `Can you provide a 7-day action plan for optimal cultivation?`;

    navigate('/vaniai', { state: { cropContext: context, cropName: crop.name } });
  };

  if (loading) {
    return (
      <div className="pt-28 min-h-screen bg-[#fafaf9] flex items-center justify-center">
        <Loader2 className="w-12 h-12 animate-spin text-[#84cc16]" />
      </div>
    );
  }

  // Handle Cultivation View Mode
  if (selected && viewMode === 'cultivation') {
    return <CultivationView crop={selected} onClose={() => setViewMode('detail')} />;
  }

  // Standard Detail View (for ALL crops including Paddy)
  if (selected) {
    return (
      <div className="pt-24 min-h-screen bg-[#fafaf9]">
        <GrainOverlay />
        <div className="max-w-6xl mx-auto px-6 pb-20">
          <button onClick={() => { setSelected(null); setViewMode('detail'); }} className="flex items-center gap-2 text-stone-400 hover:text-[#84cc16] font-bold mb-8 transition-colors text-sm">
            <ChevronLeft size={18} /> Back to Registry
          </button>

          <div className="grid lg:grid-cols-[1.5fr_1fr] gap-16">
            <div>
              {/* Hero Image */}
              <div className="relative h-[600px] rounded-[4rem] overflow-hidden mb-12 shadow-2xl group">
                <img src={selected.image} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700" alt={selected.name} />
                <div className="absolute inset-0 bg-gradient-to-t from-stone-950 via-transparent to-transparent opacity-60"></div>
                <div className="absolute bottom-16 left-16">
                  <h1 className="text-white font-serif text-[6rem] font-black leading-none mb-4">{selected.name}</h1>
                  <p className="text-[#84cc16] font-serif italic text-3xl">{selected.scientific}</p>
                  <p className="text-white/60 text-sm font-bold mt-2 uppercase tracking-wider">Variety: {selected.variety}</p>
                </div>
              </div>

              {/* KPI Ribbon */}
              <div className="grid grid-cols-3 gap-6 mb-12">
                {[
                  { label: 'MSP', value: selected.msp, icon: DollarSign, color: '#84cc16' },
                  { label: 'Cycle', value: selected.cycle, icon: Timer, color: '#facc15' },
                  { label: 'Irrigation', value: selected.water, icon: Droplets, color: '#3b82f6' },
                ].map((kpi, i) => (
                  <div key={i} className="bg-white p-6 rounded-2xl border border-stone-100 shadow-lg text-center hover:-translate-y-1 transition-all">
                    <div className="p-3 rounded-lg mb-3 mx-auto w-fit" style={{ backgroundColor: `${kpi.color}20` }}>
                      <kpi.icon size={20} style={{ color: kpi.color }} />
                    </div>
                    <span className="text-[8px] font-black text-stone-400 uppercase tracking-[0.2em] block mb-2">{kpi.label}</span>
                    <span className="text-xl font-serif font-black text-[#0c0a09]">{kpi.value}</span>
                  </div>
                ))}
              </div>

              {/* Environmental Suitability */}
              <div className="bg-white rounded-2xl p-8 border border-stone-100 shadow-lg mb-8">
                <h3 className="font-serif text-2xl font-black text-[#0c0a09] mb-6">Environmental Suitability</h3>
                <div className="grid grid-cols-2 gap-4">
                  {Object.entries(selected.suitability).map(([key, value]) => (
                    <div key={key} className="bg-stone-50 rounded-lg p-4">
                      <span className="text-[8px] font-black text-stone-400 uppercase tracking-[0.2em] block mb-1">{key}</span>
                      <span className="text-base font-bold text-[#0c0a09]">{value}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Disease Matrix */}
              <div className="bg-stone-900 rounded-2xl p-8 shadow-xl mb-8">
                <div className="flex items-center gap-2 mb-6">
                  <AlertTriangle className="text-[#facc15] w-6 h-6" />
                  <h3 className="font-serif text-2xl font-black text-white">Pathogen Database</h3>
                </div>
                <div className="space-y-4">
                  {selected.diseases.map((disease, i) => (
                    <div key={i} className="bg-white/5 border border-white/10 rounded-lg p-5 hover:bg-white/10 transition-all">
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <h4 className="text-white font-black text-base mb-1">{disease.name}</h4>
                          <p className="text-stone-400 text-xs italic">{disease.scientific}</p>
                        </div>
                        <span className={`px-2.5 py-1 rounded-lg text-[8px] font-black uppercase tracking-wider flex-shrink-0 ${disease.risk === 'High' || disease.risk === 'Severe' ? 'bg-red-500/20 text-red-400' :
                          disease.risk === 'Moderate' ? 'bg-yellow-500/20 text-yellow-400' :
                            'bg-green-500/20 text-green-400'
                          }`}>
                          {disease.risk}
                        </span>
                      </div>
                      <div className="space-y-2 text-xs">
                        <div>
                          <span className="text-[#84cc16] font-black uppercase tracking-widest block mb-0.5">Symptoms</span>
                          <p className="text-white/70">{disease.symptoms}</p>
                        </div>
                        <div>
                          <span className="text-[#facc15] font-black uppercase tracking-widest block mb-0.5">Treatment</span>
                          <p className="text-white/70">{disease.protocol}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Sidebar - Actions */}
            <div>
              <div className="sticky top-24 space-y-6">

                {/* [NEW] Cultivation Manager Launch Button (For Supported Crops) */}
                {['Paddy', 'Ragi', 'Coffee', 'Sugarcane', 'Tomato', 'Potato', 'Maize', 'Capsicum', 'Soybean', 'Grape', 'Orange', 'Apple'].includes(selected.name) && (
                  <button
                    onClick={() => setViewMode('cultivation')}
                    className="block w-full p-1 bg-gradient-to-br from-[#0c0a09] to-[#1c1917] rounded-2xl shadow-2xl hover:scale-[1.02] transition-all group"
                  >
                    <div className="bg-stone-900/50 backdrop-blur-xl rounded-[14px] p-8 border border-white/10 relative overflow-hidden">
                      <div className="absolute top-0 right-0 p-4 opacity-50"><Activity className="text-[#84cc16] w-24 h-24 -mr-8 -mt-8 rotate-12" /></div>
                      <div className="relative z-10">
                        <div className="w-12 h-12 bg-[#84cc16] rounded-xl flex items-center justify-center mb-4 text-[#0c0a09]">
                          <Sprout size={24} />
                        </div>
                        <h3 className="font-serif text-2xl font-black text-white mb-2 leading-tight">Cultivation<br /><span className="text-[#84cc16]">Manager</span></h3>
                        <p className="text-stone-400 text-xs font-medium mb-6">Active tracking, diagnostics, and AI guidance for your crop cycle.</p>
                        <div className="flex items-center gap-2 text-[#84cc16] text-[10px] font-black uppercase tracking-widest group-hover:gap-4 transition-all">
                          Open Dashboard <ArrowRight size={14} />
                        </div>
                      </div>
                    </div>
                  </button>
                )}

                {/* Vani AI Launch */}
                <button
                  onClick={() => handleLaunchVani(selected)}
                  className="block w-full p-8 bg-gradient-to-br from-[#84cc16] to-[#10b981] rounded-2xl shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all"
                >
                  <div className="bg-[#0c0a09] w-16 h-16 rounded-2xl flex items-center justify-center mb-6 mx-auto">
                    <MessageSquare className="text-[#84cc16] w-8 h-8" />
                  </div>
                  <h3 className="font-serif text-2xl font-black text-[#0c0a09] mb-4 text-center">Launch Advisor</h3>
                  <p className="text-[#0c0a09]/80 text-sm font-medium mb-6 text-center">Get AI-powered cultivation plan</p>
                  <div className="w-full py-4 bg-[#0c0a09] text-white text-center font-black text-[9px] uppercase tracking-widest rounded-xl">
                    Connect to Vani AI →
                  </div>
                </button>

                {/* Cultivation Context */}
                <div className="bg-white rounded-2xl p-6 border border-stone-100 shadow-lg">
                  <h4 className="font-black text-xs uppercase tracking-wider text-stone-400 mb-4">Context</h4>
                  <div className="space-y-2 text-xs">
                    <p className="text-stone-600"><span className="font-bold text-[#0c0a09]">Region:</span> {selected.region}</p>
                    <p className="text-stone-600"><span className="font-bold text-[#0c0a09]">Variety:</span> {selected.variety}</p>
                    <p className="text-stone-600"><span className="font-bold text-[#0c0a09]">Water:</span> {selected.water}</p>
                    <p className="text-stone-600"><span className="font-bold text-[#0c0a09]">Diseases:</span> {selected.diseases.length}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }


  // List View (unchanged)
  return (
    <div className="pt-24 min-h-screen bg-[#fafaf9] px-6 pb-20">
      <GrainOverlay />
      <header className="mb-16 text-center max-w-2xl mx-auto">
        <SectionLabel text="Agricultural Database" icon={Dna} />
        <h1 className="font-serif text-5xl font-black text-[#0c0a09] mb-4">Crop <span className="italic text-[#84cc16]">Intelligence.</span></h1>
        <p className="text-stone-500 text-base font-medium">Disease mapping and cultivation guidance for Karnataka</p>
      </header>

      <div className="grid lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
        {crops.map((crop) => (
          <div
            key={crop.id}
            onClick={() => setSelected(crop)}
            className="group cursor-pointer bg-white rounded-2xl overflow-hidden border border-stone-100 shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all duration-500"
          >
            <div className="h-56 overflow-hidden relative">
              <img src={crop.image} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" alt={crop.name} />
              <div className="absolute inset-0 bg-gradient-to-t from-stone-950/70 via-transparent to-transparent"></div>
              <div className="absolute bottom-4 left-6">
                <span className="px-3 py-1.5 bg-[#84cc16] text-[9px] font-black text-[#0c0a09] rounded-lg uppercase tracking-wider">{crop.variety}</span>
              </div>
            </div>
            <div className="p-6">
              <h3 className="font-serif text-2xl font-black text-[#0c0a09]">{crop.name}</h3>
              <p className="text-stone-400 text-sm mb-4">{crop.scientific}</p>
              <button className="text-[#84cc16] font-bold text-xs uppercase tracking-wider">Access Knowledge Core &rarr;</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const GrainOverlay = () => <div className="grain-overlay opacity-30" />;
const SectionLabel = ({ text, icon: Icon }) => (
  <div className="flex items-center gap-2 mb-6 opacity-60">
    {Icon && <Icon size={12} className="text-[#84cc16]" />}
    <span className="text-[10px] font-black uppercase tracking-[0.4em] text-[#0c0a09]">{text}</span>
  </div>
);

// --- Mock price data for chart ---
const PRICE_DATA = [
  { month: 'Jan', price: 1850 },
  { month: 'Feb', price: 1920 },
  { month: 'Mar', price: 2100 },
  { month: 'Apr', price: 2050 },
  { month: 'May', price: 2200 },
  { month: 'Jun', price: 2350 },
];

// --- Crop Data ---
const CROPS = [
  { id: 1, name: 'Paddy', scientific: 'Oryza sativa', variety: 'Hybrid-4', region: 'Cauvery Basin', msp: '₹2,183', cycle: '120 Days', water: 'High', yield: '25q/acre', image: 'C:\\Users\\Yashas H D\\Desktop\\PYTHON\\5\\backend\\images\\paddy.jpg' },
  { id: 2, name: 'Ragi', scientific: 'Eleusine coracana', variety: 'GPU-28', region: 'Dry Zone', msp: '₹3,846', cycle: '110 Days', water: 'Low', yield: '15q/acre', image: 'C:\\Users\\Yashas H D\\Desktop\\PYTHON\\5\\backend\\images\\ragi.jpg' },
  { id: 3, name: 'Coffee', scientific: 'Coffea arabica', variety: 'Sln.795', region: 'Malnad Highlands', msp: 'Market', cycle: 'Perennial', water: 'Moderate', yield: '800kg/acre', image: 'C:\\Users\\Yashas H D\\Desktop\\PYTHON\\5\\backend\\images\\coffee.jpg' },
  { id: 4, name: 'Sugarcane', scientific: 'Saccharum officinarum', variety: 'Co-86032', region: 'Mandya Belt', msp: 'FRP', cycle: '12 Months', water: 'Very High', yield: '40t/acre', image: 'C:\\Users\\Yashas H D\\Desktop\\PYTHON\\5\\backend\\images\\sugarcane.jpg' }
];

// --- Navigation ---
const Navbar = () => {
  const [lang, setLang] = useState('EN');
  const location = useLocation();

  const navLinks = [
    { path: '/', label: 'Portal' },
    { path: '/diagnostics', label: 'Detection' },
    { path: '/knowledge', label: 'Knowledge' },
    { path: '/market', label: 'Market' },
    { path: '/vaniai', label: 'Vani AI' },
  ];

  return (
    <nav className="fixed top-0 w-full z-[100] h-16 px-6 flex justify-between items-center bg-white/90 backdrop-blur-[30px] border-b border-stone-100">
      <Link to="/" className="flex items-center gap-3">
        <div className="bg-[#0c0a09] p-2 rounded-lg shadow-2xl shadow-[#84cc16]/20 hover:scale-110 transition-transform">
          <Sprout className="text-[#84cc16] w-5 h-5" />
        </div>
        <div className="flex flex-col">
          <span className="font-serif font-black text-lg tracking-tight text-[#0c0a09] leading-none">
            Krishi<span className="italic text-[#84cc16]">Vigyan</span>
          </span>
          <span className="text-[7px] font-black tracking-[0.2em] uppercase opacity-40">Intelligence</span>
        </div>
      </Link>

      <div className="hidden lg:flex items-center gap-6">
        {navLinks.map((link) => (
          <Link
            key={link.path}
            to={link.path}
            className="group relative"
          >
            <div className={`text-[9px] font-black tracking-[0.15em] uppercase ${location.pathname === link.path ? 'text-[#84cc16]' : 'text-stone-400 group-hover:text-[#0c0a09]'}`}>
              {link.label}
            </div>
            {location.pathname === link.path && (
              <motion.div layoutId="navline" className="absolute -bottom-1 w-0.5 h-0.5 bg-[#84cc16] rounded-full" />
            )}
          </Link>
        ))}
      </div>

      <div className="flex items-center gap-4">
        <Link to="/settings" className="p-2 hover:bg-stone-100 rounded-lg transition-colors opacity-40 hover:opacity-100"><Settings size={16} /></Link>
        <button
          onClick={() => setLang(lang === 'EN' ? 'KN' : 'EN')}
          className="bg-[#0c0a09] text-white px-4 py-2 rounded-lg font-black text-[9px] tracking-wider uppercase flex items-center gap-2 hover:bg-[#84cc16] hover:text-[#0c0a09] transition-all shadow-md"
        >
          <Globe className="w-3 h-3" />
          {lang}
        </button>
      </div>
    </nav>
  );
};

// --- Home ---
const HomeTerminal = () => (
  <div className="pt-20 min-h-screen bg-[#fafaf9]">
    <GrainOverlay />
    <section className="relative h-[110vh] mx-3 my-2 rounded-3xl overflow-hidden group shadow-[0_30px_60px_rgba(0,0,0,0.1)] border-2 border-white">
      <div className="absolute inset-0 bg-cover bg-center transition-transform duration-[30s] ease-linear group-hover:scale-110" style={{ backgroundImage: "url('https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&q=80&w=2000')" }}></div>
      <div className="absolute inset-0 bg-gradient-to-tr from-[#0c0a09]/95 via-[#0c0a09]/40 to-transparent"></div>
      <div className="relative h-full flex flex-col justify-center px-10 lg:px-16 py-20">
        <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 1 }}>
          <div className="flex items-center gap-2 bg-white/10 backdrop-blur-md border border-white/20 w-fit px-4 py-2 rounded-full mb-8">
            <span className="w-2 h-2 bg-[#84cc16] rounded-full animate-pulse"></span>
            <span className="text-white text-[9px] font-black tracking-[0.2em] uppercase">KrishiVigyan v5.0</span>
          </div>
          <h1 className="font-serif text-white text-6xl lg:text-8xl leading-[0.8] font-black mb-8 tracking-tight drop-shadow-2xl">
            Precision<br /><span className="text-[#84cc16] italic">Pathology.</span>
          </h1>
          <p className="font-serif text-white/80 text-lg lg:text-2xl font-medium max-w-2xl mb-12 leading-relaxed italic border-l-4 border-[#84cc16] pl-6">
            Agricultural intelligence network for Karnataka.
          </p>
          <div className="flex flex-wrap gap-6 items-center">
            <Link to="/diagnostics" className="bg-[#84cc16] text-[#0c0a09] px-10 py-4 rounded-2xl font-black text-base uppercase tracking-tighter shadow-2xl hover:bg-[#facc15] transition-all hover:scale-105 flex items-center gap-3 group">
              Enter Terminal <ScanLine className="w-5 h-5 group-hover:rotate-12 transition-transform" />
            </Link>
          </div>
        </motion.div>
      </div>
    </section>

    <section className="max-w-6xl mx-auto px-6 py-20 grid lg:grid-cols-3 gap-6">
      <Link to="/diagnostics" className="relative group overflow-hidden rounded-2xl bg-white border border-stone-100 shadow-lg hover:shadow-2xl transition-all duration-700 flex flex-col p-8 lg:col-span-2">
        <div className="p-3 rounded-2xl w-fit mb-6 bg-[#84cc16]/20"><Dna size={28} className="text-[#84cc16]" /></div>
        <h3 className="font-serif text-4xl font-black text-[#0c0a09] mb-4">Molecular <span className="italic opacity-30">Detection</span></h3>
        <p className="text-stone-500 text-base font-medium mb-6">Recursive neural match against 1,200+ pathogen strains.</p>
        <div className="mt-auto flex items-center gap-3 text-[9px] font-black uppercase tracking-[0.2em] text-[#84cc16]">
          Execute <ArrowUpRight size={14} />
        </div>
      </Link>
      <Link to="/knowledge" className="relative group overflow-hidden rounded-2xl bg-white border border-stone-100 shadow-lg hover:shadow-2xl transition-all duration-700 flex flex-col p-8">
        <div className="p-3 rounded-2xl w-fit mb-6 bg-[#10b981]/20"><BookOpen size={28} className="text-[#10b981]" /></div>
        <h3 className="font-serif text-4xl font-black text-[#0c0a09] mb-4">Knowledge <span className="italic opacity-30">Core</span></h3>
        <p className="text-stone-500 text-base font-medium mb-6">Crop encyclopedia.</p>
        <div className="mt-auto flex items-center gap-3 text-[9px] font-black uppercase tracking-[0.2em] text-[#10b981]">
          Execute <ArrowUpRight size={14} />
        </div>
      </Link>
      <Link to="/market" className="relative group overflow-hidden rounded-2xl bg-white border border-stone-100 shadow-lg hover:shadow-2xl transition-all duration-700 flex flex-col p-8">
        <div className="p-3 rounded-2xl w-fit mb-6 bg-[#facc15]/20"><TrendingUp size={28} className="text-[#facc15]" /></div>
        <h3 className="font-serif text-4xl font-black text-[#0c0a09] mb-4">Market <span className="italic opacity-30">Intel</span></h3>
        <p className="text-stone-500 text-base font-medium mb-6">Live price intelligence.</p>
        <div className="mt-auto flex items-center gap-3 text-[9px] font-black uppercase tracking-[0.2em] text-[#facc15]">
          Execute <ArrowUpRight size={14} />
        </div>
      </Link>
      <Link to="/vaniai" className="relative group overflow-hidden rounded-2xl bg-white border border-stone-100 shadow-lg hover:shadow-2xl transition-all duration-700 flex flex-col p-8 lg:col-span-2">
        <div className="p-3 rounded-2xl w-fit mb-6 bg-[#3b82f6]/20"><MessageSquare size={28} className="text-[#3b82f6]" /></div>
        <h3 className="font-serif text-4xl font-black text-[#0c0a09] mb-4">Vani <span className="italic opacity-30">AI</span></h3>
        <p className="text-stone-500 text-base font-medium mb-6">Multilingual advisor.</p>
        <div className="mt-auto flex items-center gap-3 text-[9px] font-black uppercase tracking-[0.2em] text-[#3b82f6]">
          Launch <ArrowUpRight size={16} />
        </div>
      </Link>
    </section>
  </div>
);

// --- Market Intelligence Hub ---
const MarketHub = () => {
  const [selectedCrop, setSelectedCrop] = useState('Paddy');
  const [marketData, setMarketData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [kpis, setKpis] = useState({ msp: '₹2,183', supply_index: 94, trend: 'Bullish', trend_percent: '+2.4%', forecast_percent: '+5.1%' });
  const [priceHistory, setPriceHistory] = useState([
    { month: 'Jul', price: 1950 }, { month: 'Aug', price: 2050 }, { month: 'Sep', price: 2100 },
    { month: 'Oct', price: 2080 }, { month: 'Nov', price: 2150 }, { month: 'Dec', price: 2183 }
  ]);

  const fetchMarketData = async () => {
    setLoading(true);
    try {
      const res = await axios.post('http://localhost:5000/api/market-data', {
        crop: selectedCrop,
        region: 'Karnataka'
      });
      setMarketData(res.data);
      // Update KPIs and price history from backend response
      if (res.data.kpis) setKpis(res.data.kpis);
      if (res.data.price_history) setPriceHistory(res.data.price_history);
    } catch (err) {
      console.error('Market data fetch failed:', err);
      setMarketData({ analysis: 'Unable to fetch live data. Please try again.', sources: [] });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="pt-28 min-h-screen bg-[#0c0a09] px-10">
      <GrainOverlay />
      <div className="max-w-screen-2xl mx-auto pb-40">
        {/* Header */}
        <header className="mb-16">
          <h1 className="font-serif text-7xl font-black text-white mb-8">
            Market <span className="text-[#facc15]">Intelligence.</span>
          </h1>
          <p className="text-stone-400 text-xl">Real-time APMC data for Karnataka markets</p>
        </header>

        <div className="grid lg:grid-cols-[1fr_400px] gap-10">
          {/* Main Area */}
          <div>
            {/* Dynamic KPI Tiles */}
            <div className="grid grid-cols-3 gap-6 mb-10">
              <div className="bg-white/10 p-8 rounded-3xl border border-white/20">
                <p className="text-stone-400 text-sm mb-2 uppercase tracking-wider">MSP Floor</p>
                <p className="text-white text-3xl font-black">{kpis.msp}</p>
                <p className="text-[#84cc16] text-xs font-bold mt-2">{kpis.trend_percent}</p>
              </div>
              <div className="bg-white/10 p-8 rounded-3xl border border-white/20">
                <p className="text-stone-400 text-sm mb-2 uppercase tracking-wider">Supply Index</p>
                <p className="text-white text-3xl font-black">{kpis.supply_index}</p>
                <p className="text-stone-500 text-xs font-bold mt-2">Stable</p>
              </div>
              <div className="bg-white/10 p-8 rounded-3xl border border-white/20">
                <p className="text-stone-400 text-sm mb-2 uppercase tracking-wider">Trend</p>
                <p className="text-white text-3xl font-black">{kpis.trend}</p>
                <p className="text-[#10b981] text-xs font-bold mt-2">{kpis.forecast_percent}</p>
              </div>
            </div>

            {/* Dynamic Price Chart - Professional Dual View */}
            <div className="bg-white/5 rounded-[4rem] p-10 border border-white/10">
              <div className="mb-8">
                <h3 className="text-white text-2xl font-black mb-2">6-Month Price Trajectory</h3>
                <p className="text-stone-400 text-sm font-medium">Market trends and price movement analysis</p>
              </div>

              <div className="grid lg:grid-cols-2 gap-8">
                {/* Left: Data Table */}
                <div className="bg-stone-950 rounded-2xl p-6 border border-white/10">
                  <h4 className="text-[#facc15] font-black text-sm mb-4 uppercase tracking-wider">Price Data</h4>
                  <div className="space-y-3">
                    {priceHistory.map((data, i) => (
                      <div key={i} className="flex items-center justify-between p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-all">
                        <div className="flex items-center gap-3">
                          <div className="w-2 h-2 bg-[#84cc16] rounded-full"></div>
                          <span className="text-white font-bold text-sm">{data.month}</span>
                        </div>
                        <span className="text-[#facc15] font-black text-sm">₹{data.price.toLocaleString()}</span>
                      </div>
                    ))}
                  </div>

                  {/* Summary Stats */}
                  <div className="mt-6 pt-6 border-t border-white/10 space-y-3">
                    <div className="flex justify-between text-xs">
                      <span className="text-stone-400">Highest:</span>
                      <span className="text-[#10b981] font-black">₹{Math.max(...priceHistory.map(d => d.price)).toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-stone-400">Lowest:</span>
                      <span className="text-red-400 font-black">₹{Math.min(...priceHistory.map(d => d.price)).toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-stone-400">Change:</span>
                      <span className={`font-black ${priceHistory[priceHistory.length - 1].price > priceHistory[0].price ? 'text-[#10b981]' : 'text-red-400'}`}>
                        {((priceHistory[priceHistory.length - 1].price - priceHistory[0].price) / priceHistory[0].price * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                </div>

                {/* Right: Visual Chart */}
                <div className="bg-stone-950 rounded-2xl p-6 border border-white/10">
                  <h4 className="text-[#84cc16] font-black text-sm mb-4 uppercase tracking-wider">Trend Chart</h4>
                  <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={priceHistory} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                      <defs>
                        <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#84cc16" stopOpacity={0.8} />
                          <stop offset="95%" stopColor="#84cc16" stopOpacity={0.1} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                      <XAxis dataKey="month" stroke="#999" style={{ fontSize: '12px' }} />
                      <YAxis stroke="#999" style={{ fontSize: '12px' }} />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'rgba(0,0,0,0.8)',
                          border: '1px solid #84cc16',
                          borderRadius: '8px'
                        }}
                        formatter={(value) => `₹${value.toLocaleString()}`}
                        labelStyle={{ color: '#fff' }}
                      />
                      <Area type="monotone" dataKey="price" stroke="#84cc16" strokeWidth={3} fillOpacity={1} fill="url(#colorPrice)" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div>
            <div className="bg-stone-950 rounded-[3.5rem] p-10 border-2 border-stone-800 sticky top-32">
              <h3 className="text-white text-2xl font-black mb-6">AI Neural Uplink</h3>

              <select
                value={selectedCrop}
                onChange={(e) => setSelectedCrop(e.target.value)}
                className="w-full bg-white/5 border-2 border-white/10 rounded-2xl p-5 text-white font-bold mb-6 outline-none focus:ring-2 focus:ring-[#facc15]"
              >
                {CROPS.map(crop => (
                  <option key={crop.id} value={crop.name} className="bg-stone-950">{crop.name}</option>
                ))}
              </select>

              <button
                onClick={fetchMarketData}
                disabled={loading}
                className="w-full bg-gradient-to-r from-[#facc15] to-[#84cc16] text-[#0c0a09] font-black py-6 rounded-3xl mb-8 hover:shadow-[0_20px_60px_rgba(250,204,21,0.4)] transition-all shadow-2xl disabled:opacity-50 flex items-center justify-center gap-3"
              >
                {loading ? (
                  <><Loader2 className="w-5 h-5 animate-spin" /> Loading...</>
                ) : (
                  <><Radio className="w-5 h-5" /> Execute Search</>
                )}
              </button>

              {marketData && (
                <div className="space-y-6">
                  <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
                    <h4 className="text-[#facc15] font-bold text-sm mb-3 uppercase tracking-wider">AI Analysis</h4>
                    <p className="text-white text-sm leading-relaxed">{marketData.analysis}</p>
                  </div>

                  {marketData.sources && marketData.sources.length > 0 && (
                    <div>
                      <h4 className="text-[#facc15] font-bold text-xs mb-3 uppercase tracking-wider">Sources</h4>
                      <div className="space-y-2">
                        {marketData.sources.map((src, i) => (
                          <a
                            key={i}
                            href={src.uri}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-2 bg-white/5 border border-white/10 rounded-xl p-3 hover:bg-white/10 transition-all text-xs text-stone-400 hover:text-white"
                          >
                            <ExternalLink className="w-3 h-3 text-[#facc15] flex-shrink-0" />
                            <span className="truncate">{src.title}</span>
                          </a>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};


// --- Vani AI ---
const VaniAI = () => {
  const location = useLocation();
  const cropContext = location.state?.cropContext;
  const cropName = location.state?.cropName;

  const [messages, setMessages] = useState(() => {
    const defaultMsg = { role: 'model', content: 'Welcome. I am Vani AI, your agricultural advisor from UAS Dharwad. How can I help you today?' };
    if (cropContext) {
      return [
        defaultMsg,
        { role: 'user', content: cropContext }
      ];
    }
    return [defaultMsg];
  });
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [playingAudioIndex, setPlayingAudioIndex] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Auto-fetch AI response if context was provided
    if (cropContext && messages.length === 2) {
      handleContextResponse();
    }
  }, []);

  const handleContextResponse = async () => {
    setLoading(true);
    try {
      const res = await axios.post('http://localhost:5000/api/chat', {
        message: cropContext,
        history: [{ role: 'model', content: 'Welcome. I am Vani AI, your agricultural advisor from UAS Dharwad. How can I help you today?' }]
      });
      setMessages(prev => [...prev, { role: 'model', content: res.data.response }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'model', content: "I'm currently experiencing technical difficulties. However, I can still assist you based on my training. Please proceed with your questions." }]);
    } finally {
      setLoading(false);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMsg = input;
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setInput('');
    setLoading(true);

    try {
      const res = await axios.post('http://localhost:5000/api/chat', {
        message: userMsg,
        history: messages
      });
      setMessages(prev => [...prev, { role: 'model', content: res.data.response }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'model', content: "Neural link interrupted." }]);
    } finally {
      setLoading(false);
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const handleTextToSpeech = (text, messageIndex) => {
    try {
      // Check if Web Speech API is available
      const SpeechSynthesisUtterance = window.SpeechSynthesisUtterance || window.webkitSpeechSynthesisUtterance;
      if (!SpeechSynthesisUtterance) {
        alert('Speech synthesis not supported in this browser');
        setPlayingAudioIndex(null);
        return;
      }

      // Stop any currently playing audio
      window.speechSynthesis.cancel();

      // Small delay to ensure cancel completes
      setTimeout(() => {
        // Create speech utterance
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'en-US';
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;

        // Set playing state
        setPlayingAudioIndex(messageIndex);

        console.log('Speaking:', text.substring(0, 50) + '...');

        // Handle end of speech
        utterance.onstart = () => {
          console.log('Speech started');
        };

        utterance.onend = () => {
          console.log('Speech ended');
          setPlayingAudioIndex(null);
        };

        utterance.onerror = (event) => {
          console.error('Speech synthesis error:', event.error);
          setPlayingAudioIndex(null);
          alert('Audio playback error: ' + event.error);
        };

        // Speak the text
        window.speechSynthesis.speak(utterance);
      }, 100);

    } catch (err) {
      console.error('TTS error:', err);
      setPlayingAudioIndex(null);
      alert('Error: ' + err.message);
    }
  };

  return (
    <div className="pt-20 h-screen bg-[#0c0a09] overflow-hidden flex flex-col">
      <GrainOverlay />

      <div className="flex-1 overflow-y-auto px-6 pt-16 pb-32 scrollbar-hide">
        <div className="max-w-3xl mx-auto space-y-8">
          {messages.map((m, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-[75%] p-6 rounded-2xl ${m.role === 'user' ? 'bg-stone-900 text-white' : 'bg-white/10 backdrop-blur-xl border border-white/10 text-stone-200'}`}>
                <p className="text-sm leading-relaxed font-medium">{m.content}</p>
                {m.role === 'model' && (
                  <div className="mt-4 pt-4 border-t border-white/5 flex items-center gap-3">
                    <button
                      onClick={() => handleTextToSpeech(m.content, i)}
                      className={`p-2 rounded-lg transition-all ${playingAudioIndex === i ? 'bg-[#84cc16] text-[#0c0a09]' : 'bg-white/5 hover:bg-[#84cc16] hover:text-[#0c0a09]'}`}
                      title="Click to listen"
                    >
                      <Volume2 size={14} />
                    </button>
                    <span className="text-[8px] font-black uppercase tracking-widest text-[#84cc16]">{playingAudioIndex === i ? 'Playing...' : 'Audio'}</span>
                  </div>
                )}
              </div>
            </motion.div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-white/10 backdrop-blur-xl p-6 rounded-2xl border border-white/10 flex items-center gap-3">
                <div className="flex gap-1">{[0, 150, 300].map((delay) => (<div key={delay} className="w-1.5 h-1.5 bg-[#84cc16] rounded-full animate-bounce" style={{ animationDelay: `${delay}ms` }}></div>))}</div>
                <span className="text-[8px] font-black uppercase text-[#84cc16] tracking-widest">Thinking</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 w-full max-w-3xl px-6">
        <div className="bg-white/10 backdrop-blur-xl p-4 rounded-2xl border border-white/20 shadow-[0_30px_60px_rgba(0,0,0,0.6)] flex items-center gap-3">
          <button className="w-10 h-10 rounded-full flex items-center justify-center bg-[#84cc16] hover:scale-105 transition-all shadow-lg"><Mic className="text-[#0c0a09] w-5 h-5" /></button>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask Vani AI..."
            className="flex-1 bg-transparent border-none outline-none text-white text-sm placeholder:text-stone-500 font-medium"
          />
          <button onClick={handleSend} className="p-2.5 bg-white/5 hover:bg-white/10 rounded-lg text-white transition-all hover:scale-105 group"><Send size={16} className="group-hover:text-[#84cc16]" /></button>
        </div>
      </div>
    </div>
  );
};

// --- Settings & Neural Configuration Terminal ---
const SettingsTerminal = () => {
  const [localLang, setLocalLang] = useState('EN');
  const [cropCluster, setCropCluster] = useState('All Karnataka');
  const [notifications, setNotifications] = useState(true);
  const [priceAlerts, setPriceAlerts] = useState(true);
  const [saved, setSaved] = useState(false);
  const [saving, setSaving] = useState(false);
  const [cacheSize, setCacheSize] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load settings from backend
  React.useEffect(() => {
    const loadSettings = async () => {
      try {
        setLoading(true);
        const response = await axios.get('http://localhost:5000/api/settings');
        if (response.data.success) {
          const settings = response.data.settings;
          setLocalLang(settings.language || 'EN');
          setCropCluster(settings.crop_cluster || 'All Karnataka');
          setNotifications(settings.notifications !== false);
          setPriceAlerts(settings.price_alerts !== false);
        }
      } catch (err) {
        logger.error('Failed to load settings:', err);
        setError('Failed to load settings from server');
        // Fall back to localStorage
        setLocalLang(localStorage.getItem('lang') || 'EN');
        setCropCluster(localStorage.getItem('cropCluster') || 'All Karnataka');
        setNotifications(localStorage.getItem('notifications') === 'true' || true);
        setPriceAlerts(localStorage.getItem('priceAlerts') === 'true' || true);
      } finally {
        setLoading(false);
      }
    };

    loadSettings();

    // Calculate cache size
    let total = 0;
    for (let key in localStorage) {
      if (key.startsWith('analysis_') || key.startsWith('crop_')) {
        total += (localStorage[key].length + key.length) * 2; // rough bytes
      }
    }
    setCacheSize(Math.round(total / 1024)); // KB
  }, []);

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);

      const response = await axios.post('http://localhost:5000/api/settings', {
        language: localLang,
        crop_cluster: cropCluster,
        notifications: notifications,
        price_alerts: priceAlerts
      });

      if (response.data.success) {
        // Also update localStorage as fallback
        localStorage.setItem('lang', localLang);
        localStorage.setItem('cropCluster', cropCluster);
        localStorage.setItem('notifications', notifications);
        localStorage.setItem('priceAlerts', priceAlerts);

        setSaved(true);
        setTimeout(() => setSaved(false), 2000);
        setTimeout(() => window.location.reload(), 500); // Reload to apply changes
      } else {
        setError(response.data.error || 'Failed to save settings');
      }
    } catch (err) {
      logger.error('Error saving settings:', err);
      setError('Failed to save settings to server');
    } finally {
      setSaving(false);
    }
  };

  const handlePurgeCache = () => {
    const keys = Object.keys(localStorage).filter(k => k.startsWith('analysis_') || k.startsWith('crop_'));
    keys.forEach(k => localStorage.removeItem(k));
    setCacheSize(0);
    alert('Neural cache purged successfully');
  };

  const handleResetSettings = async () => {
    if (window.confirm('Are you sure you want to reset all settings to default values?')) {
      try {
        setSaving(true);
        const response = await axios.post('http://localhost:5000/api/settings/reset');

        if (response.data.success) {
          const settings = response.data.settings;
          setLocalLang(settings.language || 'EN');
          setCropCluster(settings.crop_cluster || 'All Karnataka');
          setNotifications(settings.notifications !== false);
          setPriceAlerts(settings.price_alerts !== false);

          // Update localStorage
          localStorage.setItem('lang', settings.language);
          localStorage.setItem('cropCluster', settings.crop_cluster);
          localStorage.setItem('notifications', settings.notifications);
          localStorage.setItem('priceAlerts', settings.price_alerts);

          alert('Settings reset to defaults');
          setTimeout(() => window.location.reload(), 500);
        }
      } catch (err) {
        logger.error('Error resetting settings:', err);
        alert('Failed to reset settings');
      } finally {
        setSaving(false);
      }
    }
  };

  const Toggle = ({ checked, onChange, label }) => (
    <div className="flex items-center justify-between p-6 bg-stone-50 rounded-2xl border border-stone-200 hover:border-[#84cc16]/30 transition-all">
      <span className="font-bold text-stone-700">{label}</span>
      <button
        onClick={() => onChange(!checked)}
        className={`relative w-16 h-8 rounded-full transition-all shadow-inner ${checked ? 'bg-[#84cc16]' : 'bg-stone-300'}`}
      >
        <div className={`absolute top-1 w-6 h-6 bg-white rounded-full shadow-lg transition-all ${checked ? 'right-1' : 'left-1'}`}>
          {checked && <div className="absolute inset-0 m-auto w-2 h-2 bg-[#84cc16] rounded-full animate-pulse"></div>}
        </div>
      </button>
    </div>
  );

  if (loading) {
    return (
      <div className="pt-24 min-h-screen bg-[#fafaf9] px-6 pb-20 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin text-[#84cc16] mx-auto mb-4" />
          <p className="text-stone-600 font-bold">Loading settings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="pt-24 min-h-screen bg-[#fafaf9] px-6 pb-20">
      <GrainOverlay />
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <header className="mb-12">
          <SectionLabel text="Settings" icon={Settings} />
          <h1 className="font-serif text-5xl font-black text-[#0c0a09] mb-4">Control <span className="italic text-[#84cc16]">Panel.</span></h1>
          <p className="text-stone-500 text-base font-medium max-w-2xl">Configure your preferences, language, and system settings.</p>
        </header>

        {error && (
          <div className="mb-6 bg-red-50 border-2 border-red-200 rounded-2xl p-4 flex gap-3">
            <AlertTriangle size={20} className="text-red-600 flex-shrink-0 mt-0.5" />
            <p className="text-red-700 font-bold text-sm">{error}</p>
          </div>
        )}

        <div className="grid lg:grid-cols-[1fr_400px] gap-10">
          {/* Main Settings Panel */}
          <div className="space-y-6">
            {/* Regional Configuration */}
            <div className="bg-white border-2 border-stone-200 rounded-[3rem] p-10 shadow-xl">
              <div className="mb-8">
                <h3 className="text-[10px] font-black uppercase tracking-[0.4em] text-stone-400 mb-2">Regional Configuration</h3>
                <h2 className="font-serif text-4xl font-black text-[#0c0a09]">Localization Protocol</h2>
              </div>

              <div className="space-y-6">
                <div>
                  <label className="block font-black text-xs uppercase tracking-widest text-stone-500 mb-3">Primary Language</label>
                  <select
                    value={localLang}
                    onChange={(e) => setLocalLang(e.target.value)}
                    className="w-full bg-stone-50 border-2 border-stone-200 rounded-2xl p-5 font-bold text-stone-700 outline-none focus:ring-4 focus:ring-[#84cc16]/10 focus:border-[#84cc16] transition-all"
                  >
                    <option value="EN">English (Default)</option>
                    <option value="KN">ಕನ್ನಡ (Kannada)</option>
                    <option value="TE">తెలుగు (Telugu)</option>
                    <option value="TA">தமிழ் (Tamil)</option>
                    <option value="HI">हिन्दी (Hindi)</option>
                  </select>
                </div>

                <div>
                  <label className="block font-black text-xs uppercase tracking-widest text-stone-500 mb-3">Crop Cluster Region</label>
                  <select
                    value={cropCluster}
                    onChange={(e) => setCropCluster(e.target.value)}
                    className="w-full bg-stone-50 border-2 border-stone-200 rounded-2xl p-5 font-bold text-stone-700 outline-none focus:ring-4 focus:ring-[#84cc16]/10 focus:border-[#84cc16] transition-all"
                  >
                    <option value="All Karnataka">All Karnataka (Statewide)</option>
                    <option value="North Karnataka">North Karnataka (Hubli, Belagavi)</option>
                    <option value="South Karnataka">South Karnataka (Bangalore, Mandya)</option>
                    <option value="Coastal Karnataka">Coastal Karnataka (Mangalore, Udupi)</option>
                    <option value="Malnad">Malnad Highlands (Coffee Belt)</option>
                  </select>
                  <p className="text-xs text-stone-400 mt-2 font-medium">This affects APMC mandi prioritization in Market Intelligence</p>
                </div>
              </div>
            </div>

            {/* Notification Preferences */}
            <div className="bg-white border-2 border-stone-200 rounded-[3rem] p-10 shadow-xl">
              <div className="mb-8">
                <h3 className="text-[10px] font-black uppercase tracking-[0.4em] text-stone-400 mb-2">Alert System</h3>
                <h2 className="font-serif text-4xl font-black text-[#0c0a09]">Notification Matrix</h2>
              </div>

              <div className="space-y-4">
                <Toggle checked={notifications} onChange={setNotifications} label="Pathogen Detection Alerts" />
                <Toggle checked={priceAlerts} onChange={setPriceAlerts} label="Market Price Notifications" />
              </div>
            </div>

            {/* Action Buttons */}
            <div className="space-y-3">
              <button
                onClick={handleSave}
                disabled={saved || saving}
                className={`w-full py-6 rounded-3xl font-black text-lg uppercase tracking-wider shadow-2xl transition-all flex items-center justify-center gap-2 ${saved
                  ? 'bg-[#10b981] text-white'
                  : saving
                    ? 'bg-[#84cc16]/50 text-[#0c0a09] cursor-wait'
                    : 'bg-[#84cc16] text-[#0c0a09] hover:bg-[#facc15] hover:scale-[1.02]'
                  }`}
              >
                {saving && <Loader2 size={18} className="animate-spin" />}
                {saved ? '✓ Configuration Saved' : 'Save Configuration'}
              </button>

              <button
                onClick={handleResetSettings}
                disabled={saving}
                className="w-full py-4 rounded-2xl font-bold text-sm uppercase tracking-wider bg-stone-100 text-stone-700 hover:bg-stone-200 transition-all border-2 border-stone-300"
              >
                Reset to Defaults
              </button>
            </div>
          </div>

          {/* Sidebar - Neural Cache & Privacy */}
          <div className="space-y-6">
            {/* Storage Overview */}
            <div className="bg-stone-900 border-2 border-stone-800 rounded-[3rem] p-10 shadow-2xl sticky top-32">
              <div className="mb-8">
                <h3 className="text-[10px] font-black uppercase tracking-[0.4em] text-[#facc15] mb-2">Data Sovereignty</h3>
                <h2 className="font-serif text-3xl font-black text-white mb-4">Neural Cache</h2>
                <p className="text-stone-400 text-sm font-medium">Local diagnostic history and metadata storage.</p>
              </div>

              <div className="space-y-6">
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs font-black uppercase tracking-widest text-stone-500">Cache Usage</span>
                    <span className="text-white font-black">{cacheSize} KB</span>
                  </div>
                  <div className="h-3 bg-white/10 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-[#84cc16] to-[#facc15] transition-all duration-1000"
                      style={{ width: `${Math.min((cacheSize / 100) * 100, 100)}%` }}
                    ></div>
                  </div>
                  <p className="text-xs text-stone-500 mt-2 font-medium">Limit: ~5MB browser storage</p>
                </div>

                <button
                  onClick={handlePurgeCache}
                  className="w-full bg-red-600 text-white py-5 rounded-2xl font-black text-sm uppercase tracking-wider hover:bg-red-700 transition-all shadow-xl flex items-center justify-center gap-3"
                >
                  <AlertTriangle size={18} />
                  Purge Diagnostic Cache
                </button>

                <div className="pt-6 border-t border-white/10">
                  <h4 className="text-white font-black text-sm mb-3">Privacy Statement</h4>
                  <p className="text-stone-400 text-xs leading-relaxed">All diagnostic data is stored locally on your device. No analysis results are transmitted to external servers. You maintain complete sovereignty over your agricultural intelligence footprint.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// --- Diagnostics ---
const DiagnosticsTerminal = () => {
  const [image, setImage] = useState(null);
  const [imageFile, setImageFile] = useState(null);
  const [activeStep, setActiveStep] = useState(0);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImage(URL.createObjectURL(file));
      setImageFile(file);
      setActiveStep(1);
      setResult(null);
    }
  };

  const handleExecuteScan = async () => {
    if (!imageFile) return;
    setLoading(true);
    setActiveStep(2);
    const formData = new FormData();
    formData.append('image', imageFile);

    try {
      setTimeout(() => setActiveStep(3), 600);
      const res = await axios.post('http://localhost:5000/api/analyze-image', formData);
      setActiveStep(4);
      setTimeout(() => { setResult(res.data); setActiveStep(5); setLoading(false); }, 400);
    } catch (err) {
      console.error('Scan failed:', err);
      setActiveStep(1);
      setLoading(false);
    }
  };

  const resetScanner = () => { setImage(null); setImageFile(null); setResult(null); setActiveStep(0); setLoading(false); };

  return (
    <div className="pt-24 px-6 pb-20 min-h-screen bg-[#fafaf9]">
      <GrainOverlay />
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <header className="mb-12 text-center max-w-2xl mx-auto">
          <SectionLabel text="Pathology Detection" icon={Dna} />
          <h1 className="font-serif text-5xl font-black text-[#0c0a09] mb-4">Disease <span className="italic text-[#84cc16]">Scanner.</span></h1>
          <p className="text-stone-500 text-base font-medium">Upload a crop image for instant AI-powered disease detection</p>
        </header>

        <div className="grid lg:grid-cols-[1fr_320px] gap-8">
          {/* Main Scanner */}
          <div className={`relative bg-[#0c0a09] rounded-2xl border-2 border-white shadow-lg overflow-hidden flex flex-col items-center justify-center transition-all ${activeStep >= 2 ? 'ring-2 ring-[#84cc16]/30' : ''}`} style={{ height: '500px' }}>
            {!image ? (
              <div onClick={() => fileInputRef.current.click()} className="cursor-pointer text-center p-12 w-full h-full flex flex-col items-center justify-center group hover:bg-[#84cc16]/5 transition-colors">
                <div className="w-24 h-24 bg-white/5 border-2 border-dashed border-white/20 rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:border-[#84cc16]/40">
                  <Upload className="w-12 h-12 text-white/40 group-hover:text-[#84cc16]" />
                </div>
                <h3 className="font-serif text-3xl font-black text-white mb-3">Disease Scanner</h3>
                <p className="font-sans text-stone-400 text-sm max-w-sm">Upload a crop image to detect diseases, pests, and conditions instantly</p>
              </div>
            ) : (
              <div className="relative w-full h-full flex flex-col items-center justify-center p-6">
                <div className="relative w-full flex-1 rounded-lg overflow-hidden border-2 border-white/20 shadow-lg mb-4">
                  <motion.img src={image} animate={{ scale: activeStep >= 2 && activeStep < 5 ? 1.05 : 1 }} className="w-full h-full object-cover" alt="Scan" />
                  {(activeStep >= 2 && activeStep < 5) && (
                    <div className="absolute inset-0 bg-gradient-to-r from-[#84cc16]/20 via-transparent to-[#84cc16]/20 animate-pulse"></div>
                  )}
                </div>
                {activeStep === 1 && (
                  <button
                    onClick={handleExecuteScan}
                    disabled={loading}
                    className="w-full py-4 bg-[#84cc16] text-[#0c0a09] font-black text-base rounded-lg flex items-center justify-center gap-3 hover:bg-[#facc15] shadow-lg disabled:opacity-50 transition-all"
                  >
                    {loading ? <Loader2 size={16} className="animate-spin" /> : <Play size={16} className="fill-[#0c0a09]" />}
                    {loading ? 'SCANNING...' : 'EXECUTE SCAN'}
                  </button>
                )}
                {activeStep >= 2 && (
                  <div className="flex items-center gap-2 text-[#84cc16] text-xs font-black uppercase tracking-widest">
                    <div className="w-1.5 h-1.5 bg-[#84cc16] rounded-full animate-pulse"></div>
                    Analyzing...
                  </div>
                )}
                <button onClick={resetScanner} className="absolute top-4 right-4 p-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 transition-colors">
                  <RefreshCw size={16} />
                </button>
              </div>
            )}
          </div>

          {/* Results Sidebar */}
          <div className="space-y-4">
            {!result ? (
              <div className="bg-white rounded-2xl p-6 border border-stone-100 shadow-lg text-center">
                <Dna className="w-8 h-8 text-[#84cc16] mx-auto mb-3 opacity-30" />
                <p className="text-stone-400 text-xs font-bold uppercase tracking-wider">Ready for scan</p>
              </div>
            ) : (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
                {/* Disease Card */}
                <div className="bg-gradient-to-br from-[#84cc16]/10 to-[#facc15]/10 rounded-2xl p-6 border-2 border-[#84cc16]/30 shadow-lg">
                  <h2 className="font-serif text-xl font-black text-[#0c0a09] mb-1">{result.disease_name || 'Unknown'}</h2>
                  <p className="text-stone-500 font-serif italic text-xs mb-4">{result.scientific_name || 'N/A'}</p>

                  {/* Confidence Score */}
                  <div className="flex items-center gap-2 mb-4">
                    <Zap className="w-3.5 h-3.5 text-[#84cc16]" />
                    <span className="text-[#84cc16] font-black text-sm">{result.confidence_score || 0}% Confidence</span>
                  </div>

                  {/* Risk Level */}
                  <div className="text-[8px] font-black uppercase tracking-wider text-stone-500 mb-3">Risk Level</div>
                  <div className="bg-[#0c0a09]/40 rounded-lg p-3 mb-4">
                    <p className="text-white text-sm font-bold">
                      {result.confidence_score >= 80 ? '🔴 High Risk' : result.confidence_score >= 50 ? '🟡 Moderate' : '🟢 Low Risk'}
                    </p>
                  </div>
                </div>

                {/* Treatment */}
                <div className="bg-white rounded-2xl p-6 border border-stone-100 shadow-lg">
                  <h3 className="text-[8px] font-black text-stone-400 uppercase tracking-wider mb-3">Recommended Treatment</h3>
                  <p className="text-[#84cc16] font-bold text-sm mb-3">
                    {Array.isArray(result.remedial_organic) ? result.remedial_organic[0] : result.remedial_organic}
                  </p>
                  {result.remedial_chemical && (
                    <div className="text-[8px] text-stone-500">
                      <span className="font-bold block mb-1">Chemical:</span>
                      {Array.isArray(result.remedial_chemical) ? result.remedial_chemical[0] : result.remedial_chemical}
                    </div>
                  )}
                </div>

                {/* Economic Impact */}
                {result.economic_impact_inr && (
                  <div className="bg-red-50 rounded-2xl p-4 border border-red-100">
                    <p className="text-[8px] font-black text-stone-600 uppercase tracking-wider mb-1">Economic Impact</p>
                    <p className="text-red-600 font-black text-sm">{result.economic_impact_inr}</p>
                  </div>
                )}
              </motion.div>
            )}

            {/* Action Button */}
            <button
              onClick={() => fileInputRef.current.click()}
              className="w-full py-3 bg-[#0c0a09] text-white font-black text-xs uppercase tracking-widest rounded-lg hover:bg-[#1a1815] transition-colors"
            >
              {image && result ? 'Scan Another' : 'Upload Image'}
            </button>
          </div>
        </div>

        <input type="file" ref={fileInputRef} onChange={handleFileUpload} className="hidden" accept="image/*" />
      </div>
    </div>
  );
};

const App = () => (
  <Router>
    <div className="min-h-screen font-sans">
      <GrainOverlay />
      <Navbar />
      <Routes>
        <Route path="/" element={<HomeTerminal />} />
        <Route path="/diagnostics" element={<DiagnosticsTerminal />} />
        <Route path="/knowledge" element={<KnowledgeCore />} />
        <Route path="/market" element={<MarketHub />} />
        <Route path="/vaniai" element={<VaniAI />} />
        <Route path="/settings" element={<SettingsTerminal />} />
      </Routes>
    </div>
  </Router>
);

export default App;