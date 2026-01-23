import React from 'react';

const ToolCard = ({ title, description, icon, color = "from-blue-500 to-cyan-400" }) => {
    return (
        <div className="group relative p-6 bg-slate-900/40 border border-slate-800/60 rounded-2xl hover:bg-slate-800/60 hover:border-slate-700 transition-all duration-300 cursor-pointer overflow-hidden backdrop-blur-sm">
            <div className="absolute inset-0 bg-gradient-to-br from-transparent to-slate-900/50 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

            <div className="relative z-10 flex flex-col items-center text-center space-y-4">
                <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${color} p-0.5 shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                    <div className="w-full h-full bg-slate-950 rounded-2xl flex items-center justify-center">
                        <div className="text-3xl filter drop-shadow-md transform group-hover:rotate-6 transition-transform duration-300">
                            {icon}
                        </div>
                    </div>
                </div>

                <div className="space-y-1">
                    <h3 className="text-lg font-bold text-white group-hover:text-blue-400 transition-colors">
                        {title}
                    </h3>
                    <p className="text-sm text-slate-500 group-hover:text-slate-400 transition-colors line-clamp-2">
                        {description}
                    </p>
                </div>
            </div>
        </div>
    );
};

export default ToolCard;
