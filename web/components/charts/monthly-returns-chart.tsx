"use client";

import { useState, useMemo } from "react";
import {
    ResponsiveContainer,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Cell,
    ReferenceLine,
} from "recharts";
import { TimeSeriesPoint } from "@/lib/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight } from "lucide-react";

interface MonthlyReturnsChartProps {
    data: TimeSeriesPoint[];
    series: string;
    title?: string;
    className?: string;
}

export function MonthlyReturnsChart({
    data,
    series,
    title = "Monthly Returns",
    className,
}: MonthlyReturnsChartProps) {
    // Each page shows 12 months
    const [pageOffset, setPageOffset] = useState(0);
    const PAGE_SIZE = 12;

    const { displayedData, hasNext, hasPrev } = useMemo(() => {
        // Reverse to deal with end-of-list being most recent
        const total = data.length;
        const end = total - (pageOffset * PAGE_SIZE);
        const start = Math.max(0, end - PAGE_SIZE);

        return {
            displayedData: data.slice(start, end),
            hasNext: pageOffset > 0,
            hasPrev: start > 0
        };
    }, [data, pageOffset]);

    // Format period for display
    const formatTick = (period: string) => {
        const [year, month] = period.split("-");
        const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
        return `${monthNames[parseInt(month) - 1]} '${year.slice(2)}`;
    };

    return (
        <Card className={`${className} h-full`}>
            <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                    <CardTitle className="text-lg font-medium">{title}</CardTitle>
                    <div className="flex items-center gap-1">
                        <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8"
                            onClick={() => setPageOffset(prev => prev + 1)}
                            disabled={!hasPrev}
                        >
                            <ChevronLeft className="h-4 w-4" />
                        </Button>
                        <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8"
                            onClick={() => setPageOffset(prev => prev - 1)}
                            disabled={!hasNext}
                        >
                            <ChevronRight className="h-4 w-4" />
                        </Button>
                    </div>
                </div>
            </CardHeader>
            <CardContent>
                <div className="h-[250px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart
                            data={displayedData}
                            margin={{ top: 5, right: 20, left: 10, bottom: 5 }}
                        >
                            <CartesianGrid
                                strokeDasharray="3 3"
                                stroke="#3f3f46"
                                opacity={0.3}
                                vertical={false}
                            />
                            <XAxis
                                dataKey="period"
                                tickFormatter={formatTick}
                                tick={{ fill: "#a1a1aa", fontSize: 10 }}
                                axisLine={{ stroke: "#3f3f46" }}
                                tickLine={{ stroke: "#3f3f46" }}
                            />
                            <YAxis
                                tickFormatter={(value) => `${value.toFixed(0)}%`}
                                tick={{ fill: "#a1a1aa", fontSize: 10 }}
                                axisLine={{ stroke: "#3f3f46" }}
                                tickLine={{ stroke: "#3f3f46" }}
                            />
                            <Tooltip
                                cursor={{ fill: "rgba(255,255,255,0.05)" }}
                                contentStyle={{
                                    backgroundColor: "#18181b",
                                    border: "1px solid #3f3f46",
                                    borderRadius: "8px",
                                    fontSize: "12px",
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
                                formatter={(value) => {
                                    if (typeof value === "number") {
                                        return [`${value.toFixed(2)}%`, series];
                                    }
                                    return ["—", series];
                                }}
                            />
                            <ReferenceLine y={0} stroke="#52525b" />
                            <Bar dataKey={series} radius={[2, 2, 0, 0]}>
                                {displayedData.map((entry, index) => {
                                    const value = entry[series];
                                    const isPositive = typeof value === "number" && value >= 0;
                                    return (
                                        <Cell
                                            key={`cell-${index}`}
                                            fill={isPositive ? "var(--chart-2)" : "var(--destructive)"}
                                            fillOpacity={0.8}
                                        />
                                    );
                                })}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </CardContent>
        </Card>
    );
}
