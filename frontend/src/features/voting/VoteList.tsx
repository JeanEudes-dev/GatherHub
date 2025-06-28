import React, { useEffect, useState } from 'react'
import { useVotingStore } from '../../store/votingStore'
import type { Vote } from '../../services/votingService'
import VoteItem from './VoteItem'
import CreateVoteForm from './CreateVoteForm'
import VoteModal from './VoteModal'
import { Button } from '../../components/ui/button'
import { PlusCircle } from 'lucide-react'
import { useAuthStore } from '../../store/authStore'
import { motion } from 'framer-motion'

interface VoteListProps {
  eventId: number
  isEventCreator: boolean // Passed from EventDetailPage
}

const VoteList: React.FC<VoteListProps> = ({ eventId, isEventCreator }) => {
  const { votes, fetchVotesByEvent, isLoading, error } = useVotingStore()
  const isAuthenticated = useAuthStore(state => state.isAuthenticated())

  const [isCreateVoteFormOpen, setIsCreateVoteFormOpen] = useState(false)
  const [selectedVote, setSelectedVote] = useState<Vote | null>(null) // For VoteModal
  const [isVoteModalOpen, setIsVoteModalOpen] = useState(false)

  useEffect(() => {
    if (eventId) {
      fetchVotesByEvent(eventId)
    }
  }, [eventId, fetchVotesByEvent])

  const handleOpenCreateVoteForm = () => {
    setIsCreateVoteFormOpen(true)
  }

  const handleCloseCreateVoteForm = () => {
    setIsCreateVoteFormOpen(false)
    fetchVotesByEvent(eventId); // Refetch votes after creating one
  }

  const handleSelectVote = (vote: Vote) => {
    setSelectedVote(vote) // Store will fetch full details if needed via fetchVoteById
    setIsVoteModalOpen(true)
  }

  const handleCloseVoteModal = () => {
    setIsVoteModalOpen(false)
    setSelectedVote(null)
    fetchVotesByEvent(eventId); // Refetch to update list summary if vote was cast etc.
  }

  if (isLoading && votes.length === 0) {
    return (
      <div className="py-6 text-center text-gray-400">Loading votes...</div>
    )
  }

  if (error) {
    return (
      <div className="py-6 text-center text-red-400">
        Error loading votes: {error}
      </div>
    )
  }

  const eventSpecificVotes = votes.filter(vote => vote.event.id === eventId)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-2xl font-semibold text-white">Votes & Polls</h3>
        {isEventCreator && isAuthenticated && (
          <Button
            onClick={handleOpenCreateVoteForm}
            className="btn-glass text-sm"
          >
            <PlusCircle size={18} className="mr-2" /> Create Vote
          </Button>
        )}
      </div>

      {eventSpecificVotes.length === 0 && !isLoading && (
        <div className="glass-card rounded-md p-6 text-center">
          <p className="text-gray-400">
            No votes or polls have been created for this event yet.
          </p>
          {isEventCreator && isAuthenticated && (
            <Button
              onClick={handleOpenCreateVoteForm}
              variant="link"
              className="mt-2 text-aurora-blue"
            >
              Create the first vote
            </Button>
          )}
        </div>
      )}

      {eventSpecificVotes.length > 0 && (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {eventSpecificVotes.map((vote, index) => (
            <motion.div
              key={vote.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
            >
              <VoteItem vote={vote} onSelectVote={handleSelectVote} />
            </motion.div>
          ))}
        </div>
      )}

      {isEventCreator && isAuthenticated && (
        <CreateVoteForm
          isOpen={isCreateVoteFormOpen}
          onClose={handleCloseCreateVoteForm}
          eventId={eventId}
        />
      )}

      <VoteModal
        isOpen={isVoteModalOpen}
        onClose={handleCloseVoteModal}
        vote={selectedVote}
      />
    </div>
  )
}

export default VoteList
