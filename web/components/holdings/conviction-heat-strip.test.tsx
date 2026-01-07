import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ConvictionHeatStrip } from './conviction-heat-strip'
import { PeriodPerformance } from '@/lib/types'

describe('ConvictionHeatStrip', () => {
    it('renders net return correctly', () => {
        const mockData: PeriodPerformance = {
            summary: {
                net_return: 0.124,
                gainers_count: 15,
                losers_count: 10,
                avg_return: 0.08,
            },
            holdings: [
                {
                    symbol: 'AAPL',
                    current_price: 150,
                    period_start_price: 130,
                    period_return: 0.15,
                    allocation: 0.2,
                    total_return_pct: 0.5,
                },
                {
                    symbol: 'GOOGL',
                    current_price: 100,
                    period_start_price: 120,
                    period_return: -0.17,
                    allocation: 0.15,
                    total_return_pct: 0.2,
                },
            ],
        }

        render(<ConvictionHeatStrip performance={mockData} />)

        // Check that the net return is displayed
        expect(screen.getByText(/\+12\.4%/)).toBeInTheDocument()
        expect(screen.getByText(/Weighted Net Return/i)).toBeInTheDocument()
    })

    it('renders nothing when no holdings', () => {
        const mockData: PeriodPerformance = {
            summary: {
                net_return: 0,
                gainers_count: 0,
                losers_count: 0,
                avg_return: 0,
            },
            holdings: [],
        }

        const { container } = render(<ConvictionHeatStrip performance={mockData} />)
        expect(container.firstChild).toBeNull()
    })
})
