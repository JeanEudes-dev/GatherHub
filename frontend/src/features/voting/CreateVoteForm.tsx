import React, { useState, useEffect } from 'react';
import { CreateVoteData } from '../../services/votingService';
import { useVotingStore } from '../../store/votingStore';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Textarea } from '../../components/ui/textarea';
import { Checkbox } from '../../components/ui/checkbox';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogClose } from '../../components/ui/dialog';
// import { toast } from 'sonner';
import { PlusCircle, Trash2 } from 'lucide-react';

interface CreateVoteFormProps {
  isOpen: boolean;
  onClose: () => void;
  eventId: number;
}

const CreateVoteForm: React.FC<CreateVoteFormProps> = ({ isOpen, onClose, eventId }) => {
  const { createVote, isLoading, error } = useVotingStore();

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [options, setOptions] = useState([{ text: '' }, { text: '' }]); // Start with two options
  const [endsAtDate, setEndsAtDate] = useState(''); // YYYY-MM-DD
  const [endsAtTime, setEndsAtTime] = useState(''); // HH:MM
  const [multipleChoice, setMultipleChoice] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    // Reset form when it's reopened (if not editing)
    if (isOpen) {
      setTitle('');
      setDescription('');
      setOptions([{ text: '' }, { text: '' }]);
      setEndsAtDate('');
      setEndsAtTime('');
      setMultipleChoice(false);
      setFormError(null);
    }
  }, [isOpen]);

  const handleOptionChange = (index: number, value: string) => {
    const newOptions = [...options];
    newOptions[index].text = value;
    setOptions(newOptions);
  };

  const addOption = () => {
    if (options.length < 10) { // Limit max options
      setOptions([...options, { text: '' }]);
    } else {
      // toast.info("Maximum of 10 options allowed.");
    }
  };

  const removeOption = (index: number) => {
    if (options.length > 2) { // Keep at least two options
      const newOptions = options.filter((_, i) => i !== index);
      setOptions(newOptions);
    } else {
      // toast.info("A vote must have at least two options.");
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);

    if (!title || options.some(opt => !opt.text.trim())) {
      setFormError('Title and all option texts are required.');
      return;
    }
    if (options.length < 2) {
        setFormError('A vote must have at least two options.');
        return;
    }

    let endsAtISO: string | null = null;
    if (endsAtDate && endsAtTime) {
      endsAtISO = `${endsAtDate}T${endsAtTime}:00`; // Add seconds if needed, consider timezone
    } else if (endsAtDate && !endsAtTime) {
        setFormError('Please specify a time if setting an end date.');
        return;
    }


    const voteData: CreateVoteData = {
      title,
      description,
      event: eventId,
      options: options.map(opt => ({ text: opt.text.trim() })),
      ends_at: endsAtISO,
      multiple_choice: multipleChoice,
    };

    const newVote = await createVote(voteData, eventId);

    if (newVote) {
      // toast.success('Vote created successfully!');
      onClose();
    } else {
      setFormError(error || 'Failed to create vote.');
      // toast.error(error || 'Failed to create vote.');
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-lg glass-card text-white border-gray-700">
        <DialogHeader>
          <DialogTitle className="text-2xl text-white">Create New Vote</DialogTitle>
          <DialogDescription className="text-gray-400">
            Set up a new poll for event participants.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 py-4 max-h-[70vh] overflow-y-auto pr-2">
          <div>
            <Label htmlFor="voteTitle" className="text-gray-300">Vote Title</Label>
            <Input id="voteTitle" value={title} onChange={(e) => setTitle(e.target.value)} required className="bg-white/10 border-white/20 placeholder-gray-500"/>
          </div>
          <div>
            <Label htmlFor="voteDescription" className="text-gray-300">Description (Optional)</Label>
            <Textarea id="voteDescription" value={description} onChange={(e) => setDescription(e.target.value)} rows={2} className="bg-white/10 border-white/20 placeholder-gray-500"/>
          </div>

          <div className="space-y-2">
            <Label className="text-gray-300">Options</Label>
            {options.map((option, index) => (
              <div key={index} className="flex items-center gap-2">
                <Input
                  type="text"
                  placeholder={`Option ${index + 1}`}
                  value={option.text}
                  onChange={(e) => handleOptionChange(index, e.target.value)}
                  required
                  className="bg-white/10 border-white/20 placeholder-gray-500 flex-grow"
                />
                {options.length > 2 && (
                  <Button type="button" variant="ghost" size="icon" onClick={() => removeOption(index)} className="text-red-400 hover:text-red-300 h-8 w-8">
                    <Trash2 size={16}/>
                  </Button>
                )}
              </div>
            ))}
            <Button type="button" variant="outline" onClick={addOption} className="text-xs btn-glass mt-1">
              <PlusCircle size={14} className="mr-1" /> Add Option
            </Button>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="endsAtDate" className="text-gray-300">Ends On (Optional Date)</Label>
              <Input id="endsAtDate" type="date" value={endsAtDate} onChange={(e) => setEndsAtDate(e.target.value)} className="bg-white/10 border-white/20"/>
            </div>
            <div>
              <Label htmlFor="endsAtTime" className="text-gray-300">Ends At (Optional Time)</Label>
              <Input id="endsAtTime" type="time" value={endsAtTime} onChange={(e) => setEndsAtTime(e.target.value)} className="bg-white/10 border-white/20"/>
            </div>
          </div>

          <div className="flex items-center space-x-2 pt-2">
            <Checkbox id="multipleChoice" checked={multipleChoice} onCheckedChange={(checked) => setMultipleChoice(Boolean(checked))} className="border-gray-500 data-[state=checked]:bg-aurora-purple"/>
            <Label htmlFor="multipleChoice" className="text-sm text-gray-300">
              Allow multiple selections
            </Label>
          </div>

          {formError && <p className="text-sm text-red-400 text-center pt-2">{formError}</p>}
          <DialogFooter className="pt-6">
            <DialogClose asChild>
                <Button type="button" variant="outline" className="btn-glass">Cancel</Button>
            </DialogClose>
            <Button type="submit" className="btn-aurora" disabled={isLoading}>
              {isLoading ? 'Creating Vote...' : 'Create Vote'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default CreateVoteForm;
