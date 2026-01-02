"use client";

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
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface PerformanceChartProps {
    data: WealthPoint[];
    series: string[];
    title: string;
    className?: string;
}

export function PerformanceChart({
    data,
    series,
    title,
    className,
}: PerformanceChartProps) {
    // Format period for display (e.g., "2024-01" -> "Jan '24")
    const formatTick = (period: string) => {
        const [year, month] = period.split("-");
        const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
        return `${monthNames[parseInt(month) - 1]} '${year.slice(2)}`;
    };

    // Only show every Nth tick to avoid crowding
    const tickInterval = Math.ceil(data.length / 12);

    return (
        <Card className={className}>
            <CardHeader>
                <CardTitle className="text-lg font-medium">{title}</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="h-[400px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart
                            data={data}
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
                    Growth of $100 invested at inception
                </p>
            </CardContent>
        </Card>
    );
}
