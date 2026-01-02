"use client";

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
    // Get only the last 24 months for a cleaner view
    const recentData = data.slice(-24);

    // Format period for display
    const formatTick = (period: string) => {
        const [year, month] = period.split("-");
        const monthNames = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"];
        return `${monthNames[parseInt(month) - 1]}'${year.slice(2)}`;
    };

    return (
        <Card className={className}>
            <CardHeader>
                <CardTitle className="text-lg font-medium">{title}</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="h-[250px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart
                            data={recentData}
                            margin={{ top: 5, right: 20, left: 10, bottom: 5 }}
                        >
                            <CartesianGrid
                                strokeDasharray="3 3"
                                stroke="#3f3f46"
                                opacity={0.5}
                                vertical={false}
                            />
                            <XAxis
                                dataKey="period"
                                tickFormatter={formatTick}
                                tick={{ fill: "#a1a1aa", fontSize: 10 }}
                                axisLine={{ stroke: "#3f3f46" }}
                                tickLine={{ stroke: "#3f3f46" }}
                                interval={1}
                            />
                            <YAxis
                                tickFormatter={(value) => `${value.toFixed(0)}%`}
                                tick={{ fill: "#a1a1aa", fontSize: 12 }}
                                axisLine={{ stroke: "#3f3f46" }}
                                tickLine={{ stroke: "#3f3f46" }}
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
                                formatter={(value) => {
                                    if (typeof value === "number") {
                                        return [`${value.toFixed(2)}%`, series];
                                    }
                                    return ["—", series];
                                }}
                            />
                            <ReferenceLine y={0} stroke="#52525b" />
                            <Bar dataKey={series} radius={[2, 2, 0, 0]}>
                                {recentData.map((entry, index) => {
                                    const value = entry[series];
                                    const isPositive = typeof value === "number" && value >= 0;
                                    return (
                                        <Cell
                                            key={`cell-${index}`}
                                            fill={isPositive ? "#10b981" : "#ef4444"}
                                            opacity={0.8}
                                        />
                                    );
                                })}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </div>
                <p className="text-xs text-muted-foreground mt-2 text-center">
                    Last 24 months
                </p>
            </CardContent>
        </Card>
    );
}
