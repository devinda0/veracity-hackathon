import { Card } from '@/components/UI/Card';

import {
  Area,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

interface TrendEvent {
  date: string;
  trend?: number;
  confidence?: number;
}

interface TrendMapProps {
  data: unknown;
  title: string;
}

interface TrendPoint {
  date: string;
  trend: number;
  confidence: number;
  confidenceUpper: number;
  confidenceLower: number;
}

export function TrendMap({ data, title }: TrendMapProps) {
  const events = ((data as { events?: TrendEvent[] })?.events ?? []) as TrendEvent[];

  const chartData: TrendPoint[] = events.map((event, index) => {
    const trendValue = typeof event.trend === 'number' ? event.trend : Math.min(100, 45 + index * 9);
    const confidenceValue = typeof event.confidence === 'number' ? event.confidence : 65;
    const band = Math.max(5, (100 - confidenceValue) / 2);

    return {
      date: event.date,
      trend: Math.max(0, Math.min(100, trendValue)),
      confidence: Math.max(0, Math.min(100, confidenceValue)),
      confidenceUpper: Math.max(0, Math.min(100, trendValue + band)),
      confidenceLower: Math.max(0, Math.min(100, trendValue - band)),
    };
  });

  return (
    <Card>
      <p className="text-xs uppercase tracking-[0.22em] text-ink/45">Trendmap</p>
      <h3 className="mt-2 text-lg font-semibold">{title}</h3>

      {chartData.length > 0 ? (
        <div className="mt-4 h-[320px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 8, right: 12, left: -12, bottom: 8 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 12 }} />
              <YAxis domain={[0, 100]} tick={{ fill: '#64748b', fontSize: 12 }} />
              <Tooltip
                contentStyle={{ borderRadius: '12px', border: '1px solid #e5e7eb' }}
              />
              <Legend />
              <Area
                type="monotone"
                dataKey="confidenceUpper"
                stroke="none"
                fill="#93c5fd"
                fillOpacity={0.28}
                name="Confidence Band (Upper)"
              />
              <Area
                type="monotone"
                dataKey="confidenceLower"
                stroke="none"
                fill="#ffffff"
                fillOpacity={1}
                name="Confidence Band (Lower)"
              />
              <Line type="monotone" dataKey="trend" stroke="#3b82f6" strokeWidth={2.5} name="Trend" dot={false} />
              <Line
                type="monotone"
                dataKey="confidence"
                stroke="#10b981"
                strokeWidth={2}
                strokeDasharray="5 3"
                name="Confidence"
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="mt-4 rounded-[16px] border border-ink/8 bg-white/75 py-10 text-center text-sm text-ink/55">
          No trend data available
        </div>
      )}
    </Card>
  );
}
