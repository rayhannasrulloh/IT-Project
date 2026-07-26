import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://glzxrzltyfqisqknmtju.supabase.co';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdsenhyemx0eWZxaXNxa25tdGp1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODI3MTY5MDIsImV4cCI6MjA5ODI5MjkwMn0.pUiV7c7yFvJkpNBT7AmC2BB1Z5IzLajYBNoXAkWvslA';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
