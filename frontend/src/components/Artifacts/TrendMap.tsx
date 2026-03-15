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

import type { Artifact } from '@/stores/chatStore';
import { Card } from '@/components/UI/Card';

interface TrendPoint {
  date: string;
  trend: number;
  confidence: number;
  upper: number;
  lower: number;
}

interface TrendMapData {
  events?: Array<{
    date?: string;
    trend?: number;
    confidence?: number;
  }>;
}

interface TrendMapProps {
  artifact: Artifact;
}

export function TrendMap({ artifact }: TrendMapProps) {
  const data = (artifact.data ?? {}) as TrendMapData;

  const chartData: TrendPoint[] = (data.events ?? []).map((e) => {
    const conf = e.confidence ?? 0;
    const trend = e.trend ?? conf;
    return {
      date: e.date ?? '',
      trend,
      confidence: conf,
      upper: Math.min(100, conf + 10),
      lower: Math.max(0, conf - 10),
    };
  });

  return (
    <Card>
      <p className="text-xs uppercase tracking-[0.22em] text-ink/45">{artifact.type}</p>
      <h3 className="mt-2 text-lg font-semibold">{artifact.title}</h3>

      {chartData.length > 0 ? (
        <div className="mt-4">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} unit="%" />
              <Tooltip
                contentStyle={{ backgroundColor: '#f9fafb', border: '1px solid #e5e7eb' }}
              />
              <Legend />
              {/* Confidence band */}
              <Area
                type="monotone"
                dataKey="upper"
                stroke="none"
                fill="#93c5fd"
                fillOpacity={0.3}
                name="Confidence upper"
                legendType="none"
              />
              <Area
                type="monotone"
                dataKey="lower"
                stroke="none"
                fill="#ffffff"
                fillOpacity={1}
                name="Confidence lower"
                legendType="none"
              />
              {/* Lines */}
              <Line
                type="monotone"
                dataKey="trend"
                stroke="#3b82f6"
                strokeWidth={2}
                dot={false}
                name="Trend"
              />
              <Line
                type="monotone"
                dataKey="confidence"
                stroke="#10b981"
                strokeWidth={1.5}
                strokeDasharray="4 3"
                dot={false}
                name="Confidence"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <p className="mt-6 py-8 text-center text-sm text-ink/50">No trend data available</p>
      )}
    </Card>
  );
}
