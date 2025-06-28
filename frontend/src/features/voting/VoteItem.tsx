import React from 'react'
import type { Vote } from '../../services/votingService'
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '../../components/ui/card'
import { Button } from '../../components/ui/button'
import { Users, Clock, CheckSquare, PieChart } from 'lucide-react' // Icons

interface VoteItemProps {
  vote: Vote
  onSelectVote: (vote: Vote) => void // Callback to open details/voting modal
}

const formatDate = (dateString: string | null) => {
  if (!dateString) return 'N/A'
  try {
    return new Date(dateString).toLocaleString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    })
  } catch  {
    return dateString
  }
}

const VoteItem: React.FC<VoteItemProps> = ({ vote, onSelectVote }) => {
  const statusColor =
    vote.status === 'active' ? 'text-green-400' : 'text-gray-400'
  const statusBg =
    vote.status === 'active' ? 'bg-green-500/20' : 'bg-gray-500/20'

  return (
    <Card
      className="glass-card hover:shadow-aurora cursor-pointer overflow-hidden transition-all duration-300"
      onClick={() => onSelectVote(vote)}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <CardTitle className="text-lg font-semibold text-white">
            {vote.title}
          </CardTitle>
          <div
            className={`rounded-full px-2 py-0.5 text-xs ${statusBg} ${statusColor} capitalize`}
          >
            {vote.status}
          </div>
        </div>
        {vote.description && (
          <CardDescription className="mt-1 truncate text-xs text-gray-400">
            {vote.description}
          </CardDescription>
        )}
      </CardHeader>
      <CardContent className="space-y-1.5 pb-3 text-sm text-gray-300">
        <div className="flex items-center text-xs text-gray-400">
          <Users size={14} className="mr-1.5 text-aurora-blue" />
          <span>{vote.total_votes} Total Votes</span>
        </div>
        {vote.ends_at && (
          <div className="flex items-center text-xs text-gray-400">
            <Clock size={14} className="mr-1.5 text-aurora-purple" />
            <span>Ends: {formatDate(vote.ends_at)}</span>
          </div>
        )}
        <div className="flex items-center text-xs text-gray-400">
          <CheckSquare size={14} className="mr-1.5 text-aurora-yellow" />
          <span>{vote.options.length} Options</span>
          {vote.multiple_choice && (
            <span className="ml-1 text-xs">(Multi-choice)</span>
          )}
        </div>
      </CardContent>
      <CardFooter className="bg-white/5 p-3">
        <Button
          variant="link"
          className="h-auto p-0 text-sm text-aurora-pink"
          onClick={e => {
            e.stopPropagation()
            onSelectVote(vote)
          }}
        >
          <PieChart size={16} className="mr-1.5" /> View Details & Vote
        </Button>
      </CardFooter>
    </Card>
  )
}

export default VoteItem
