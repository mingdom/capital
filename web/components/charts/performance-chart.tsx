"use client";

import { useState, useMemo } from "react";
import {
    ResponsiveContainer,
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
} from "recharts";
import { WealthPoint } from "@/lib/types";
import { getChartColor } from "@/lib/data";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface PerformanceChartProps {
    data: WealthPoint[];
    series: string[];
    title: string;
    className?: string;
}

type TimeRange = "1M" | "3M" | "6M" | "YTD" | "1Y" | "Max";

export function PerformanceChart({
    data,
    series,
    title,
    className,
}: PerformanceChartProps) {
    const [selectedRange, setSelectedRange] = useState<TimeRange>("YTD");

    // Filter data based on selected time range
    const filteredData = useMemo(() => {
        if (!data || data.length === 0) return [];

        const now = new Date();
        const currentYear = now.getFullYear();
        const currentMonth = now.getMonth(); // 0-indexed

        let startIndex = 0;

        switch (selectedRange) {
            case "1M":
                // Show last 1 month
                startIndex = Math.max(0, data.length - 1);
                break;
            case "3M":
                // Show last 3 months
                startIndex = Math.max(0, data.length - 3);
                break;
            case "6M":
                // Show last 6 months
                startIndex = Math.max(0, data.length - 6);
                break;
            case "YTD":
                // Show from start of current year
                const ytdIndex = data.findIndex(point => {
                    const [year] = point.period.split("-");
                    return parseInt(year) === currentYear;
                });
                startIndex = ytdIndex >= 0 ? ytdIndex : 0;
                break;
            case "1Y":
                // Show last 12 months
                startIndex = Math.max(0, data.length - 12);
                break;
            case "Max":
                // Show all data
                startIndex = 0;
                break;
        }

        return data.slice(startIndex);
    }, [data, selectedRange]);

    // Calculate performance metrics for the selected range
    const performanceMetrics = useMemo(() => {
        if (!filteredData || filteredData.length < 2) return {};

        const metrics: Record<string, number> = {};
        const firstPoint = filteredData[0];
        const lastPoint = filteredData[filteredData.length - 1];

        series.forEach(name => {
            const startValue = firstPoint[name];
            const endValue = lastPoint[name];
            if (typeof startValue === "number" && typeof endValue === "number" && startValue > 0) {
                metrics[name] = ((endValue - startValue) / startValue) * 100;
            }
        });

        return metrics;
    }, [filteredData, series]);

    // Get the latest date from filtered data
    const latestDate = useMemo(() => {
        if (!filteredData || filteredData.length === 0) return "";
        const lastPeriod = filteredData[filteredData.length - 1].period;
        const [year, month] = lastPeriod.split("-");
        const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
        return `${monthNames[parseInt(month) - 1]} ${parseInt(month)}, ${year}`;
    }, [filteredData]);

    // Format period for display (e.g., "2024-01" -> "Jan '24")
    const formatTick = (period: string) => {
        const [year, month] = period.split("-");
        const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
        return `${monthNames[parseInt(month) - 1]} '${year.slice(2)}`;
    };

    // Dynamically adjust tick interval based on data length
    const tickInterval = Math.max(1, Math.ceil(filteredData.length / 8));

    const timeRanges: TimeRange[] = ["1M", "3M", "6M", "YTD", "1Y", "Max"];

    return (
        <Card className={className}>
            <CardHeader className="pb-3">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                    <div className="flex-1">
                        <h3 className="text-lg font-semibold">{title.split("(")[0].trim()}</h3>
                        <div className="flex flex-wrap items-center gap-3 mt-2 text-sm">
                            <span className="text-muted-foreground">{latestDate}</span>
                            {series.map(name => {
                                const perf = performanceMetrics[name];
                                if (perf === undefined) return null;
                                const color = getChartColor(name);
                                return (
                                    <div key={name} className="flex items-center gap-2">
                                        <div className="flex items-center gap-1.5">
                                            <div
                                                className="w-2 h-2 rounded-full"
                                                style={{ backgroundColor: color }}
                                            />
                                            <span className="font-medium">{name}:</span>
                                        </div>
                                        <span className={perf >= 0 ? "text-emerald-500" : "text-red-500"}>
                                            {perf >= 0 ? "+" : ""}{perf.toFixed(2)}%
                                        </span>
                                    </div>
                                );
                            })}
                        </div>
                    </div>

                    <div className="flex items-center gap-1 bg-muted/30 p-1 rounded-lg">
                        {timeRanges.map(range => (
                            <Button
                                key={range}
                                variant={selectedRange === range ? "default" : "ghost"}
                                size="sm"
                                onClick={() => setSelectedRange(range)}
                                className={`
                                    h-8 px-3 text-xs font-medium transition-all
                                    ${selectedRange === range
                                        ? "bg-primary text-primary-foreground shadow-sm"
                                        : "hover:bg-muted text-muted-foreground"
                                    }
                                `}
                            >
                                {range}
                            </Button>
                        ))}
                    </div>
                </div>
            </CardHeader>
            <CardContent>
                <div className="h-[200px] md:h-[280px] w-full mt-4">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart
                            data={filteredData}
                            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                        >
                            <CartesianGrid
                                strokeDasharray="3 3"
                                stroke="#3f3f46"
                                opacity={0.5}
                            />
                            <XAxis
                                dataKey="period"
                                tickFormatter={formatTick}
                                interval={tickInterval}
                                tick={{ fill: "#a1a1aa", fontSize: 12 }}
                                axisLine={{ stroke: "#3f3f46" }}
                                tickLine={{ stroke: "#3f3f46" }}
                            />
                            <YAxis
                                tickFormatter={(value) => `$${value.toFixed(0)}`}
                                tick={{ fill: "#a1a1aa", fontSize: 12 }}
                                axisLine={{ stroke: "#3f3f46" }}
                                tickLine={{ stroke: "#3f3f46" }}
                                domain={["dataMin - 10", "dataMax + 10"]}
                            />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: "#18181b",
                                    border: "1px solid #3f3f46",
                                    borderRadius: "8px",
                                    color: "#fafafa",
                                }}
                                labelFormatter={(label) => {
                                    const [year, month] = label.split("-");
                                    const monthNames = [
                                        "January", "February", "March", "April", "May", "June",
                                        "July", "August", "September", "October", "November", "December",
                                    ];
                                    return `${monthNames[parseInt(month) - 1]} ${year}`;
                                }}
                                formatter={(value, name) => {
                                    if (typeof value === "number") {
                                        return [`$${value.toFixed(2)}`, name];
                                    }
                                    return ["—", name];
                                }}
                            />
                            <Legend
                                wrapperStyle={{
                                    paddingTop: "20px",
                                }}
                            />
                            {series.map((name) => (
                                <Line
                                    key={name}
                                    type="linear"
                                    dataKey={name}
                                    stroke={getChartColor(name)}
                                    strokeWidth={name === "Mingdom" || name === "Fidelity" ? 3 : 2}
                                    dot={false}
                                    activeDot={{ r: 5 }}
                                />
                            ))}
                        </LineChart>
                    </ResponsiveContainer>
                </div>
                <p className="text-xs text-muted-foreground mt-4 text-center">
                    Growth of $100K invested at inception
                </p>
            </CardContent>
        </Card>
    );
}
