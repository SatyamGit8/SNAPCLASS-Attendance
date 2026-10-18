-- SnapClass Database Schema for Supabase
-- Copy and paste this script into Supabase SQL Editor and click RUN.

-- 1. Teachers Table
CREATE TABLE IF NOT EXISTS public.teachers (
    teacher_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Students Table
CREATE TABLE IF NOT EXISTS public.students (
    student_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL,
    face_embedding JSONB,
    voice_embedding JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Subjects Table
CREATE TABLE IF NOT EXISTS public.subjects (
    subject_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    subject_code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    section TEXT NOT NULL,
    teacher_id BIGINT REFERENCES public.teachers(teacher_id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Subject-Students (Enrollment) Table
CREATE TABLE IF NOT EXISTS public.subject_students (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    subject_id BIGINT REFERENCES public.subjects(subject_id) ON DELETE CASCADE,
    student_id BIGINT REFERENCES public.students(student_id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(subject_id, student_id)
);

-- 5. Attendance Logs Table
CREATE TABLE IF NOT EXISTS public.attendance_logs (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    subject_id BIGINT REFERENCES public.subjects(subject_id) ON DELETE CASCADE,
    student_id BIGINT REFERENCES public.students(student_id) ON DELETE CASCADE,
    timestamp TEXT NOT NULL,
    is_present BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security (RLS) & Allow public anon access for this app
ALTER TABLE public.teachers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.students ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subjects ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subject_students ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.attendance_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public all access on teachers" ON public.teachers FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow public all access on students" ON public.students FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow public all access on subjects" ON public.subjects FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow public all access on subject_students" ON public.subject_students FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow public all access on attendance_logs" ON public.attendance_logs FOR ALL USING (true) WITH CHECK (true);
