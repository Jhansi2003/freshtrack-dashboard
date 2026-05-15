import React from 'react';
import { 
  ShieldAlert, 
  Box, 
  ThermometerSnowflake, 
  RefreshCcw,
  Flag,
  ArrowRight,
  TrendingDown,
  Clock,
  PieChart as PieChartIcon
} from 'lucide-react';
import { 
  PieChart, 
  Pie, 
  Cell, 
  ResponsiveContainer, 
  Tooltip as ReTooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid
} from 'recharts';
import { motion } from 'motion/react';
import { SAMPLE_DATA } from '@/constants';
import { cn } from '@/lib/utils';

export default function RecommendationsPage() {
  // Aggregate data for recommendations
  const stats = React.useMemo(() => {
    const totalWasted = SAMPLE_DATA.reduce((acc, d) => acc + d.quantity_wasted_kg, 0);
    const totalLoss = SAMPLE_DATA.reduce((acc, d) => acc + d.loss_amount_inr, 0);
    
    const locationLoss = SAMPLE_DATA.reduce((acc: any, d) => {
      acc[d.location] = (acc[d.location] || 0) + d.loss_amount_inr;
      return acc;
    }, {});
    
    const topLocation = Object.entries(locationLoss).sort((a: any, b: any) => b[1] - a[1])[0][0];
    
    const productWaste = SAMPLE_DATA.reduce((acc: any, d) => {
      acc[d.product_name] = (acc[d.product_name] || 0) + d.quantity_wasted_kg;
      return acc;
    }, {});
    
    const topProduct = Object.entries(productWaste).sort((a: any, b: any) => b[1] - a[1])[0][0];

    const pieData = Object.entries(locationLoss).map(([name, value]) => ({ name, value }));
    const productBarData = Object.entries(productWaste)
      .map(([name, value]) => ({ name, value }))
      .sort((a,b) => (b.value as number) - (a.value as number))
      .slice(0, 5);

    return { totalWasted, totalLoss, topProduct, topLocation, pieData, productBarData };
  }, []);

  const COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#f97316', '#10b981'];

  return (
    <div className="space-y-12 animate-in fade-in duration-700 pb-20">
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold text-white tracking-tight">AI Recommendation Center</h2>
          <p className="text-text-dim text-sm">Data-driven strategies to eliminate inventory inefficiency.</p>
        </div>
        <div className="flex items-center gap-2 px-4 py-2 bg-emerald-500/10 text-emerald-500 rounded-full text-[10px] font-bold uppercase tracking-widest border border-emerald-500/20">
           Engine Status: Active
        </div>
      </header>

      {/* Strategic Cards */}
      <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <RecCard 
          icon={<ShieldAlert size={22} />} 
          title="High Waste Pivot" 
          description={`Procurement for ${stats.topProduct} is exceeding demand by 22%. Consider reduction in next batch.`}
          color="rose"
        />
        <RecCard 
          icon={<Box size={22} />} 
          title="Storage Logic" 
          description={`Optimizing bin placement in ${stats.topLocation} could reduce transit bruising by approx. 8.4%.`}
          color="blue"
        />
        <RecCard 
          icon={<ThermometerSnowflake size={22} />} 
          title="Variable Cooling" 
          description="Warehouse A detected 2°C variance. Deploy localized cooling for leaf-category items."
          color="amber"
        />
        <RecCard 
          icon={<RefreshCcw size={22} />} 
          title="FIFO Enforcement" 
          description="Priority inventory rotation required for Dairy category to avoid expiry cluster next week."
          color="emerald"
        />
      </section>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Bar Chart */}
        <div className="lg:col-span-2 bg-card p-10 rounded-3xl border border-border shadow-2xl space-y-8">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold text-white uppercase tracking-widest flex items-center gap-3">
              <TrendingDown className="text-rose-500" /> Top Loss Generators
            </h3>
            <span className="text-[9px] font-bold text-text-dim uppercase tracking-widest leading-none">Weight Wasted (KG)</span>
          </div>
          <div className="h-[320px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats.productBarData} layout="vertical" margin={{ left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="#1f2937" opacity={0.3} />
                <XAxis type="number" hide />
                <YAxis 
                  dataKey="name" 
                  type="category" 
                  axisLine={false} 
                  tickLine={false}
                  tick={{ fill: '#666', fontSize: 11, fontWeight: 600 }}
                  width={140}
                />
                <ReTooltip cursor={{fill: 'rgba(255,255,255,0.02)'}} contentStyle={{ backgroundColor: '#111', borderRadius: '12px', border: '1px solid #262626' }} />
                <Bar dataKey="value" radius={[0, 8, 8, 0]} barSize={16}>
                  {stats.productBarData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Global Distribution */}
        <div className="bg-card p-10 rounded-3xl border border-border shadow-2xl space-y-10">
          <div className="space-y-1">
            <h3 className="text-xs font-bold text-white uppercase tracking-widest flex items-center gap-3">
              <PieChartIcon className="text-brand" /> Loss Distribution
            </h3>
            <p className="text-[10px] text-text-dim font-bold uppercase tracking-widest">Financial footprint by node</p>
          </div>
          <div className="h-[240px] relative">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={stats.pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={65}
                  outerRadius={95}
                  paddingAngle={10}
                  dataKey="value"
                  stroke="none"
                >
                  {stats.pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <ReTooltip contentStyle={{ backgroundColor: '#111', border: '1px solid #262626', borderRadius: '8px' }} />
              </PieChart>
            </ResponsiveContainer>
            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none translate-y-1">
              <span className="text-[9px] font-bold text-[#666] uppercase tracking-widest">Aggregate</span>
              <span className="text-2xl font-light text-white tracking-tight">₹{(stats.totalLoss/1000).toFixed(1)}k</span>
            </div>
          </div>
          <div className="space-y-4 pt-4 border-t border-border/50">
             {stats.pieData.map((item, idx) => (
               <div key={item.name} className="flex items-center justify-between">
                 <div className="flex items-center gap-3">
                    <div className="w-2 h-2 rounded-full ring-4 ring-white/5" style={{ backgroundColor: COLORS[idx % COLORS.length] }} />
                    <span className="text-xs font-bold text-[#bbb] uppercase tracking-wider">{item.name}</span>
                 </div>
                 <span className="text-xs font-bold text-white tracking-wider">₹{item.value.toLocaleString()}</span>
               </div>
             ))}
          </div>
        </div>
      </div>

      {/* Action Plan Table */}
      <section className="bg-card rounded-3xl border border-border shadow-2xl overflow-hidden">
        <div className="p-8 flex items-center justify-between bg-white/[0.02] border-b border-border">
          <div className="flex items-center gap-5">
             <div className="p-3 bg-surface border border-border rounded-xl shadow-inner">
                <Flag className="text-brand" size={24} />
             </div>
             <div>
                <h3 className="text-lg font-bold text-white tracking-tight">Priority Interventions</h3>
                <p className="text-xs text-text-dim font-medium uppercase tracking-widest mt-1">Operational response queue.</p>
             </div>
          </div>
          <button className="text-[10px] font-bold text-brand uppercase tracking-widest hover:underline flex items-center gap-2">
             Full Inventory Logs <ArrowRight size={14} />
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="bg-white/5 text-[9px] font-bold uppercase tracking-[0.2em] text-[#666] border-b border-border">
                <th className="px-10 py-6">Status Priority</th>
                <th className="px-10 py-6">Sector</th>
                <th className="px-10 py-6">Intervention Strategy</th>
                <th className="px-10 py-6">Yield Gain</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              <ActionRow 
                priority="Critical" 
                area="Inventory Planning" 
                rec={`Reduce procurement quota for ${stats.topProduct} by 15.4%.`} 
                savings="₹12.4k Profit"
                priorityColor="rose"
              />
              <ActionRow 
                priority="High" 
                area="Thermal Logistics" 
                rec={`Relink cooling sensors in ${stats.topLocation}. Data drift detected.`} 
                savings="₹4.2k Save"
                priorityColor="amber"
              />
              <ActionRow 
                priority="Medium" 
                area="Staffing Flow" 
                rec="Optimize stock rotation shifts for peak vegetable intake hours." 
                savings="₹1.8k Save"
                priorityColor="blue"
              />
              <ActionRow 
                priority="Stabilized" 
                area="Network Models" 
                rec="Retrain Spoilage v2 model with recent humidity anomaly data." 
                savings="Baseline"
                priorityColor="slate"
              />
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

function RecCard({ icon, title, description, color }: { icon: React.ReactNode, title: string, description: string, color: 'rose' | 'blue' | 'amber' | 'emerald' }) {
  const styles = {
    rose: "bg-rose-500/5 border-rose-500/20 text-rose-500",
    blue: "bg-brand/5 border-brand/20 text-brand",
    amber: "bg-amber-500/5 border-amber-500/20 text-amber-500",
    emerald: "bg-emerald-500/5 border-emerald-500/20 text-emerald-500"
  };
  
  const iconStyles = {
    rose: "bg-rose-500/10 text-rose-500",
    blue: "bg-brand/10 text-brand",
    amber: "bg-amber-500/10 text-amber-500",
    emerald: "bg-emerald-500/10 text-emerald-500"
  };

  return (
    <motion.div 
      whileHover={{ scale: 1.02, backgroundColor: 'rgba(255,255,255,0.02)' }}
      className={cn("p-6 rounded-2xl border flex flex-col gap-5 transition-colors", styles[color])}
    >
      <div className={cn("p-3 rounded-xl w-fit border border-inherit shadow-inner", iconStyles[color])}>
        {icon}
      </div>
      <div className="space-y-2">
        <h4 className="font-bold tracking-tight text-white">{title}</h4>
        <p className="text-xs leading-relaxed font-medium opacity-70">{description}</p>
      </div>
    </motion.div>
  );
}

function ActionRow({ priority, area, rec, savings, priorityColor }: { priority: string, area: string, rec: string, savings: string, priorityColor: string }) {
  const pColors: any = {
    rose: "bg-rose-500/10 text-rose-500 border-rose-500/25",
    amber: "bg-amber-500/10 text-amber-500 border-amber-500/25",
    blue: "bg-brand/10 text-brand border-brand/25",
    slate: "bg-white/5 text-[#666] border-white/10"
  };

  return (
    <tr className="group hover:bg-white/[0.02] transition-colors">
      <td className="px-10 py-6">
        <span className={cn("text-[9px] font-bold uppercase tracking-wider px-2.5 py-1 rounded border", pColors[priorityColor])}>
          {priority}
        </span>
      </td>
      <td className="px-10 py-6 font-bold text-white text-xs whitespace-nowrap">{area}</td>
      <td className="px-10 py-6 text-[#888] text-xs font-medium max-w-sm leading-relaxed">{rec}</td>
      <td className="px-10 py-6 text-right">
        <div className="flex items-center justify-end gap-2 text-emerald-500 font-bold text-[10px] uppercase tracking-widest">
          <TrendingDown size={14} className="stroke-[3]" />
          {savings}
        </div>
      </td>
    </tr>
  );
}
