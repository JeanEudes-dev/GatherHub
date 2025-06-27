import React, { useState, useEffect, useMemo } from 'react';
import { Vote, VoteOption, CastVoteData, VoteResults } from '../../services/votingService';
import { useVotingStore } from '../../store/votingStore';
import { useAuthStore } from '../../store/authStore';
import { Button } from '../../components/ui/button';
import { RadioGroup, RadioGroupItem } from '../../components/ui/radio-group';
import { Checkbox } from '../../components/ui/checkbox';
import { Label } from '../../components/ui/label';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogClose } from '../../components/ui/dialog';
import { Progress } from '../../components/ui/progress'; // For displaying vote percentages
// import { toast } from 'sonner';
import { BarChart2, Check, X } from 'lucide-react';

interface VoteModalProps {
  isOpen: boolean;
  onClose: () => void;
  vote: Vote | null; // Full vote object passed in
}

const formatDate = (dateString: string | null) => {
  if (!dateString) return 'Ongoing indefinitely';
  try {
    return new Date(dateString).toLocaleString(undefined, {
      year: 'numeric', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit'
    });
  } catch (error) { return dateString; }
};

const VoteModal: React.FC<VoteModalProps> = ({ isOpen, onClose, vote: initialVote }) => {
  const {
    currentVote,
    currentVoteResults,
    fetchVoteById, // To refresh after voting or if initialVote is stale
    castVote,
    isLoading: isStoreLoading,
    error: storeError
  } = useVotingStore();

  const { user, isAuthenticated } = useAuthStore();
  const [selectedOptions, setSelectedOptions] = useState<number[]>([]);
  const [localError, setLocalError] = useState<string | null>(null);

  // Use currentVote from store if available and matches initialVote, otherwise use initialVote
  // This allows the modal to react to real-time updates fetched by the store
  const voteToDisplay = useMemo(() => {
    if (currentVote && initialVote && currentVote.id === initialVote.id) {
      return currentVote;
    }
    return initialVote;
  }, [currentVote, initialVote]);

  useEffect(() => {
    if (isOpen && voteToDisplay) {
      // Fetch fresh details and results when modal opens, especially if vote is active
      fetchVoteById(voteToDisplay.id);
      // Results are fetched by fetchVoteById if vote is active/ended

      // Reset local state
      setSelectedOptions(voteToDisplay.user_vote?.option_id ? [voteToDisplay.user_vote.option_id] : []); // Pre-select if already voted (single choice example)
      // For multiple choice, user_vote structure might be an array of options. Adjust accordingly.
      // The backend API_REFERENCE.md shows user_vote as { "option_id": 1, "voted_at": "..." }
      // This implies single choice voting is the primary model for user_vote tracking.
      // If multiple_choice is true, the pre-selection logic here might need adjustment if backend sends multiple user_vote objects or an array.
      // For now, assuming user_vote reflects one choice even if multiple_choice was true (e.g. the first/primary one).
      setLocalError(null);
    }
  }, [isOpen, voteToDisplay, fetchVoteById]);


  const handleOptionSelect = (optionId: number) => {
    if (voteToDisplay?.user_voted || voteToDisplay?.status === 'ended') return; // Don't allow changes if already voted or ended

    if (voteToDisplay?.multiple_choice) {
      setSelectedOptions(prev =>
        prev.includes(optionId) ? prev.filter(id => id !== optionId) : [...prev, optionId]
      );
    } else {
      setSelectedOptions([optionId]);
    }
  };

  const handleCastVote = async () => {
    if (!voteToDisplay || selectedOptions.length === 0) {
      setLocalError('Please select at least one option.');
      return;
    }
    setLocalError(null);
    const success = await castVote(voteToDisplay.id, { options: selectedOptions });
    // if (success) toast.success('Vote cast successfully!');
    // else setLocalError(storeError || 'Failed to cast vote.');
    // The store's fetchVoteById (called on open and after casting) will update voteToDisplay with new user_voted status & results
  };

  const canVote = isAuthenticated && voteToDisplay && voteToDisplay.status === 'active' && !voteToDisplay.user_voted;
  const showResults = voteToDisplay && (voteToDisplay.status === 'ended' || (voteToDisplay.user_voted && voteToDisplay.status === 'active'));

  if (!isOpen || !voteToDisplay) return null;

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-lg md:max-w-xl glass-card text-white border-gray-700 max-h-[85vh] flex flex-col">
        <DialogHeader className="flex-shrink-0">
          <DialogTitle className="text-2xl text-white">{voteToDisplay.title}</DialogTitle>
          <DialogDescription className="text-gray-400">
            {voteToDisplay.description || 'Cast your vote below.'}
            <div className="text-xs mt-1">
              Status: <span className={`capitalize font-semibold ${voteToDisplay.status === 'active' ? 'text-green-400' : 'text-gray-500'}`}>{voteToDisplay.status}</span>
              {voteToDisplay.ends_at && (<span> | Ends: {formatDate(voteToDisplay.ends_at)}</span>)}
            </div>
          </DialogDescription>
        </DialogHeader>

        <div className="flex-grow overflow-y-auto py-4 pr-2 space-y-6">
          {/* Voting Section or Message */}
          {!showResults && canVote && (
            <div className="space-y-3">
              <h3 className="text-md font-semibold text-gray-200 mb-1">Select your choice{voteToDisplay.multiple_choice ? '(s)' : ''}:</h3>
              {voteToDisplay.options.map(option => (
                <div key={option.id} className={`flex items-center space-x-3 p-3 rounded-md transition-all ${selectedOptions.includes(option.id!) ? 'bg-aurora-purple/30 ring-2 ring-aurora-purple' : 'bg-white/10 hover:bg-white/20'}`}>
                  {voteToDisplay.multiple_choice ? (
                    <Checkbox
                      id={`option-${option.id}`}
                      checked={selectedOptions.includes(option.id!)}
                      onCheckedChange={() => handleOptionSelect(option.id!)}
                      className="border-gray-500 data-[state=checked]:bg-aurora-purple data-[state=checked]:text-white"
                    />
                  ) : (
                    <RadioGroup value={selectedOptions[0]?.toString()} onValueChange={(val) => handleOptionSelect(Number(val))}>
                      <RadioGroupItem value={option.id!.toString()} id={`option-${option.id}`} className="border-gray-500 text-aurora-purple ring-aurora-purple focus:ring-aurora-purple data-[state=checked]:border-aurora-purple"/>
                    </RadioGroup>
                  )}
                  <Label htmlFor={`option-${option.id}`} className="text-sm font-medium text-gray-100 flex-grow cursor-pointer">
                    {option.text}
                  </Label>
                </div>
              ))}
            </div>
          )}

          {voteToDisplay.user_voted && voteToDisplay.status === 'active' && !showResults && (
             <div className="text-center p-4 bg-green-500/10 rounded-md">
                <Check size={24} className="mx-auto text-green-400 mb-2"/>
                <p className="text-green-300">You have already voted in this poll.</p>
                <p className="text-xs text-gray-400">Results will be shown once the poll ends or if the creator shares them.</p>
             </div>
          )}
           {voteToDisplay.status === 'ended' && !showResults && ( // Should typically show results if ended
             <div className="text-center p-4 bg-gray-500/10 rounded-md">
                <X size={24} className="mx-auto text-gray-400 mb-2"/>
                <p className="text-gray-300">This poll has ended.</p>
             </div>
          )}


          {/* Results Section */}
          {showResults && currentVoteResults && (
            <div className="space-y-3">
              <h3 className="text-md font-semibold text-gray-200 flex items-center"><BarChart2 size={18} className="mr-2 text-aurora-blue"/>Vote Results ({currentVoteResults.total_votes} total votes)</h3>
              {currentVoteResults.results.sort((a,b) => (b.vote_count || 0) - (a.vote_count || 0) ).map(option => (
                <div key={option.id} className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-200">{option.text}</span>
                    <span className="text-gray-400">{option.vote_count || 0} votes ({option.percentage?.toFixed(1) || 0}%)</span>
                  </div>
                  <Progress value={option.percentage || 0} className="h-2 [&>*]:bg-gradient-to-r [&>*]:from-aurora-blue [&>*]:to-aurora-purple" />
                </div>
              ))}
              {currentVoteResults.winner && (
                <p className="text-center text-lg font-semibold text-aurora-green pt-3">Winner: {currentVoteResults.winner.text}</p>
              )}
            </div>
          )}
          {isStoreLoading && (showResults || canVote) && <p className="text-sm text-center text-gray-400">Loading latest data...</p>}
        </div>

        <DialogFooter className="pt-4 flex-shrink-0">
          {localError && <p className="text-sm text-red-400 text-left flex-grow ">{localError}</p>}
          {storeError && !localError && <p className="text-sm text-red-400 text-left flex-grow">{storeError}</p>}

          <DialogClose asChild>
            <Button type="button" variant="outline" className="btn-glass">Close</Button>
          </DialogClose>
          {canVote && (
            <Button
              type="button"
              onClick={handleCastVote}
              className="btn-aurora"
              disabled={isStoreLoading || selectedOptions.length === 0}
            >
              {isStoreLoading ? 'Submitting...' : 'Submit Vote'}
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default VoteModal;
