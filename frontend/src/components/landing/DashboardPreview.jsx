import React from 'react';
import { TrendingUp, PieChart, DollarSign, Activity } from 'lucide-react';

const DashboardPreview = () => {
    // Assuming activeTab is defined elsewhere or will be added. For now, hardcoding to 0 for display.
    const activeTab = 0;

    return (
        <div className="relative w-full max-w-[600px] aspect-[4/3] mx-auto perspective-1000">
            {/* Main Dashboard Card - White on Dark Background (QB Style) */}
            <div className={`relative w-full h-full bg-white rounded-xl shadow-2xl border border-gray-200 overflow-hidden transition-all duration-700 transform ${activeTab === 0 ? 'rotate-y-0 opacity-100' : 'rotate-y-12 opacity-0 absolute top-0'}`}>
                {/* Header */}
                <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100 bg-gray-50/50">
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-red-400"></div>
                        <div className="w-3 h-3 rounded-full bg-yellow-400"></div>
                        <div className="w-3 h-3 rounded-full bg-green-400"></div>
                    </div>
                    <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Financial Overview</div>
                </div>

                {/* Body Content */}
                <div className="p-6">
                    <div className="flex items-end justify-between mb-8">
                        <div>
                            <div className="text-sm text-gray-500 mb-1">Total Revenue</div>
                            <div className="text-3xl font-bold text-gray-800">$124,500</div>
                            <div className="text-xs text-green-500 flex items-center gap-1 mt-1">
                                <TrendingUp size={12} /> +12.5% vs last month
                            </div>
                        </div>
                        <div className="text-right">
                            <div className="text-sm text-gray-500 mb-1">Efficiency</div>
                            <div className="text-xl font-bold text-gray-800">98.2%</div>
                        </div>
                    </div>

                    {/* Chart Bars Animation */}
                    <div className="h-32 flex items-end justify-between gap-2">
                        {[40, 65, 45, 80, 55, 90, 70].map((h, i) => (
                            <div key={i} className="w-full bg-gray-100 rounded-t-sm relative group overflow-hidden">
                                <div
                                    className="absolute bottom-0 w-full bg-brand-primary/80 transition-all duration-1000 ease-out group-hover:bg-brand-primary"
                                    style={{ height: `${h}%`, transitionDelay: `${i * 100}ms` }}
                                ></div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Floating UI Card 1: Revenue */}
            <div
                className="absolute top-[10%] -left-[5%] w-48 p-4 glass-effect bg-white/80 rounded-xl shadow-lg border border-white/50 z-20"
            >
                <div className="flex items-center gap-3 mb-2">
                    <div className="p-2 bg-green-100 rounded-lg text-green-600">
                        <DollarSign size={18} />
                    </div>
                    <span className="text-sm text-gray-500 font-medium">Revenue</span>
                </div>
                <div className="text-2xl font-bold text-gray-800">$124,500</div>
                <div className="text-xs text-green-600 flex items-center gap-1">
                    <TrendingUp size={12} /> +12.5% vs last month
                </div>
            </div>

            {/* Floating UI Card 2: Analysis */}
            <div
                className="absolute bottom-[20%] -right-[5%] w-44 p-4 glass-effect bg-white/80 rounded-xl shadow-lg border border-white/50 z-20"
            >
                <div className="flex items-center gap-3 mb-2">
                    <div className="p-2 bg-purple-100 rounded-lg text-purple-600">
                        <Activity size={18} />
                    </div>
                    <span className="text-sm text-gray-500 font-medium">Efficiency</span>
                </div>
                <div className="text-xl font-bold text-gray-800">98.2%</div>
                <div className="w-full h-2 bg-gray-100 rounded-full mt-2 overflow-hidden">
                    <div
                        style={{ width: '98%' }}
                        className="h-full bg-brand-primary rounded-full"
                    />
                </div>
            </div>

        </div>
    );
};

export default DashboardPreview;
