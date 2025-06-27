import { create } from 'zustand';
import {
  listVotes as apiListVotes,
  createVote as apiCreateVote,
  getVoteDetails as apiGetVoteDetails,
  castVote as apiCastVote,
  getVoteResults as apiGetVoteResults,
  Vote,
  CreateVoteData,
  CastVoteData,
  VoteResults,
  PaginatedVotesResponse
} from '../services/votingService';
import { useEventStore } from './eventStore'; // For context if needed

interface VotingState {
  votes: Vote[]; // Votes for a specific event, or all if global view
  currentVote: Vote | null;
  currentVoteResults: VoteResults | null;
  isLoading: boolean;
  error: string | null;
  pagination: { // If listing votes globally
    count: number;
    next: string | null;
    previous: string | null;
    currentPage: number;
    pageSize: number;
  };

  // Actions
  fetchVotesByEvent: (eventId: number, params?: Record<string, any>) => Promise<void>;
  fetchVoteById: (voteId: number) => Promise<Vote | null>;
  createVote: (voteData: CreateVoteData, eventId: number) => Promise<Vote | null>;
  castVote: (voteId: number, optionsData: CastVoteData) => Promise<boolean>;
  fetchVoteResults: (voteId: number) => Promise<VoteResults | null>;
  // updateVote, deleteVote if implemented

  // Real-time updates (placeholders)
  handleVoteCreated: (vote: Vote) => void;
  handleVoteUpdated: (vote: Vote) => void; // e.g., if status changes, or new vote cast
  handleVoteDeleted: (voteId: number, eventId?: number) => void;
  handleVoteResultsUpdated: (results: VoteResults) => void;
}

export const useVotingStore = create<VotingState>((set, get) => ({
  votes: [],
  currentVote: null,
  currentVoteResults: null,
  isLoading: false,
  error: null,
  pagination: {
    count: 0,
    next: null,
    previous: null,
    currentPage: 1,
    pageSize: 10,
  },

  fetchVotesByEvent: async (eventId: number, params?: Record<string, any>) => {
    set({ isLoading: true, error: null });
    try {
      const response: PaginatedVotesResponse = await apiListVotes({ ...params, event: eventId });
      set({
        votes: response.results,
        isLoading: false,
        pagination: {
            ...get().pagination,
            count: response.count,
            next: response.next,
            previous: response.previous,
            currentPage: params?.page || 1,
        }
      });
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to fetch votes';
      set({ isLoading: false, error: errorMessage, votes: [] });
    }
  },

  fetchVoteById: async (voteId: number) => {
    set({ isLoading: true, error: null, currentVote: null, currentVoteResults: null }); // Reset results too
    try {
      const vote = await apiGetVoteDetails(voteId);
      set({ currentVote: vote, isLoading: false });
      // Optionally fetch results if vote is active or ended
      if (vote.status === 'active' || vote.status === 'ended') {
        get().fetchVoteResults(voteId);
      }
      return vote;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to fetch vote details';
      set({ isLoading: false, error: errorMessage });
      return null;
    }
  },

  createVote: async (voteData: CreateVoteData, eventId: number) => {
    set({ isLoading: true, error: null });
    try {
      const newVote = await apiCreateVote(voteData);
      // Add to votes list if relevant or refetch
      if (voteData.event === eventId) {
         set(state => ({ votes: [newVote, ...state.votes] }));
      }
      // await get().fetchVotesByEvent(eventId); // Or refetch for consistency
      set({ isLoading: false });
      return newVote;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to create vote';
      set({ isLoading: false, error: errorMessage });
      return null;
    }
  },

  castVote: async (voteId: number, optionsData: CastVoteData) => {
    set({ isLoading: true, error: null });
    try {
      await apiCastVote(voteId, optionsData);
      // Refetch vote details to update user_voted status and potentially results
      await get().fetchVoteById(voteId);
      // await get().fetchVoteResults(voteId); // Also refetch results
      set({ isLoading: false });
      return true;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to cast vote';
      set({ isLoading: false, error: errorMessage });
      return false;
    }
  },

  fetchVoteResults: async (voteId: number) => {
    set({ isLoading: true, error: null }); // Can be a separate loading state for results if needed
    try {
      const results = await apiGetVoteResults(voteId);
      set({ currentVoteResults: results, isLoading: false });
      return results;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to fetch vote results';
      set({ isLoading: false, error: errorMessage, currentVoteResults: null });
      return null;
    }
  },

  // WebSocket Handlers
  handleVoteCreated: (newVote: Vote) => {
    set(state => {
      if (!state.votes.find(v => v.id === newVote.id)) {
        const currentEventId = useEventStore.getState().currentEvent?.id;
        if (currentEventId && newVote.event.id === currentEventId) {
          return { votes: [newVote, ...state.votes] };
        }
      }
      return {};
    });
  },

  handleVoteUpdated: (updatedVote: Vote) => { // E.g. when a vote is cast, or status changes
    set(state => ({
      votes: state.votes.map(vote => vote.id === updatedVote.id ? updatedVote : vote),
      currentVote: state.currentVote?.id === updatedVote.id ? updatedVote : state.currentVote,
    }));
    // If the updated vote is the current one, also refresh its results
    if (get().currentVote?.id === updatedVote.id) {
      get().fetchVoteResults(updatedVote.id);
    }
  },

  handleVoteResultsUpdated: (results: VoteResults) => {
    // This might be triggered by a specific "vote_results_updated" WS message
    // or after a "vote_cast" message if the backend sends full results.
    if (get().currentVote?.id === results.id) {
        set({ currentVoteResults: results });
    }
    // Update total_votes in the main vote object if it's part of results and differs
    set(state => ({
        votes: state.votes.map(v => v.id === results.id ? {...v, total_votes: results.total_votes, options: results.results.map(r => ({id: r.id, text: r.text, vote_count: r.vote_count})) } : v),
        currentVote: state.currentVote?.id === results.id ? {...state.currentVote, total_votes: results.total_votes, options: results.results.map(r => ({id: r.id, text: r.text, vote_count: r.vote_count}))} : state.currentVote
    }))

  },

  handleVoteDeleted: (voteId: number, eventId?: number) => { // If delete is implemented
    set(state => ({
      votes: state.votes.filter(vote => vote.id !== voteId),
      currentVote: state.currentVote?.id === voteId ? null : state.currentVote,
      currentVoteResults: state.currentVoteResults?.id === voteId ? null : state.currentVoteResults,
    }));
  },
}));
