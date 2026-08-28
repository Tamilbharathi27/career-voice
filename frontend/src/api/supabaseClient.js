import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://nmxhyfyuzvmatpdszxee.supabase.co';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'sb_publishable_Fxw_B0t7XJ8F38K-v56RjQ_zp38Y6uK';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
