export type UserRole = "administrator" | "examiner" | "candidate";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  token_type: string;
}

export type ExamStatus = "draft" | "published" | "ongoing" | "completed";
export type QuestionType = "single_mcq" | "multi_select" | "written";
export type Difficulty = "easy" | "medium" | "hard";
export type DisputeStatus = "submitted" | "under_review" | "resolved" | "rejected";

export interface Examination {
  id: string;
  title: string;
  instructions: string;
  status: ExamStatus;
  scheduled_start: string;
  scheduled_end: string;
  duration_minutes: number;
  total_marks: number;
  passing_marks: number;
  randomize_questions: boolean;
  randomize_choices: boolean;
  created_by: string;
  created_at: string;
}

export interface Question {
  id: string;
  question_text: string;
  question_type: QuestionType;
  difficulty: Difficulty;
  category: string;
  marks: number;
  choices?: Choice[];
  correct_answer_ids?: string[];
  model_answer?: string;
  created_by: string;
}

export interface Choice {
  id: string;
  choice_text: string;
  is_correct: boolean;
}

export interface Attempt {
  id: string;
  exam_id: string;
  candidate_id: string;
  started_at: string;
  submitted_at?: string;
  deadline: string;
  status: "in_progress" | "submitted" | "expired";
  total_score?: number;
}

export interface Dispute {
  id: string;
  attempt_id: string;
  candidate_id: string;
  category: string;
  description: string;
  status: DisputeStatus;
  submitted_at: string;
  resolved_at?: string;
  resolution_note?: string;
  original_score?: number;
  revised_score?: number;
}
