import React from 'react';
import { Search, Bell, Calendar as CalendarIcon, ChevronDown } from 'lucide-react';

const Header = () => {
    return (
        <header className="h-20 bg-slate-950/80 backdrop-blur-md border-b border-slate-800/50 flex items-center justify-between px-8 fixed top-0 left-64 right-0 z-10 transition-all duration-300">
            <div className="relative w-96 font-sans">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input
                    type="text"
                    placeholder="Search tools, projects, documents..."
                    className="w-full bg-slate-900/50 border border-slate-700 rounded-xl pl-10 pr-4 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all"
                />
            </div>

            <div className="flex items-center gap-6">
                <button className="relative p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors">
                    <CalendarIcon className="w-5 h-5" />
                </button>
                <button className="relative p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors">
                    <Bell className="w-5 h-5" />
                    <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full ring-2 ring-slate-950"></span>
                </button>

                <div className="flex items-center gap-3 pl-6 border-l border-slate-800">
                    <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-purple-500 to-blue-500 flex items-center justify-center text-sm font-bold text-white shadow-lg ring-2 ring-slate-800">
                        {(window.django?.user?.username || 'U').substring(0, 2).toUpperCase()}
                    </div>
                    <div className="flex items-center gap-2 cursor-pointer group">
                        <span className="text-sm font-medium text-slate-200 group-hover:text-white">
                            {window.django?.user?.username || 'User'}
                        </span>
                        <ChevronDown className="w-4 h-4 text-slate-400 group-hover:text-white transition-transform group-hover:rotate-180" />
                    </div>
                </div>
            </div>
        </header>
    );
};

export default Header;
