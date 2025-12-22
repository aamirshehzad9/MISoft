import React from 'react';
import { TrendingUp, PieChart, DollarSign, Activity } from 'lucide-react';

const DashboardPreview = () => {
    return (
        <div className="relative w-full h-[500px] flex items-center justify-center">
            {/* Main Dashboard Card Mockup */}
            <div
                className="w-full max-w-[600px] h-[380px] glass-effect rounded-2xl shadow-2xl overflow-hidden border border-white/40 bg-white/40 backdrop-blur-xl relative z-10"
            >
                {/* Mockup Header */}
                <div className="h-12 border-b border-white/20 flex items-center px-4 gap-2">
                    <div className="w-3 h-3 rounded-full bg-red-400"></div>
                    <div className="w-3 h-3 rounded-full bg-yellow-400"></div>
                    <div className="w-3 h-3 rounded-full bg-green-400"></div>
                </div>

                {/* Mockup Body - Grid */}
                <div className="p-6 grid grid-cols-2 gap-4">
                    {/* Chart Area */}
                    <div className="col-span-2 h-32 bg-white/30 rounded-lg p-4 relative overflow-hidden">
                        <div className="absolute inset-0 flex items-end justify-between px-6 pb-4 opacity-50">
                            {[40, 70, 50, 90, 60, 80, 50].map((h, i) => (
                                <div
                                    key={i}
                                    style={{ height: `${h}%` }}
                                    className="w-4 bg-brand-primary rounded-t-sm"
                                />
                            ))}
                        </div>
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
