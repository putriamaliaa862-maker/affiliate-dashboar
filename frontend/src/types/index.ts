export interface Studio {
  id: number
  name: string
  location?: string
  description?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Employee {
  id: number
  studio_id: number
  name: string
  email: string
  phone?: string
  role: 'host' | 'leader' | 'supervisor' | 'director'
  salary_base: number
  hire_date?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Attendance {
  id: number
  employee_id: number
  date: string
  check_in?: string
  check_out?: string
  status: 'present' | 'absent' | 'late' | 'sick'
  notes?: string
  created_at: string
}

export interface ShopeeAccount {
  id: number
  studio_id: number
  account_name: string
  shopee_account_id: string
  is_active: boolean
  created_at: string
}

export interface Campaign {
  id: number
  shopee_account_id: number
  campaign_name: string
  budget: number
  spent: number
  start_date: string
  end_date: string
  status: 'active' | 'paused' | 'ended'
}

export interface Order {
  id: number
  shopee_account_id: number
  order_id: string
  total_amount: number
  commission_amount: number
  status: string
  date: string
}

export interface Commission {
  id: number
  employee_id: number
  period: string
  total_amount: number
  status: 'calculated' | 'approved' | 'paid'
  paid_date?: string
  notes?: string
}

export interface Report {
  id: number
  studio_id: number
  report_type: 'daily' | 'weekly' | 'monthly'
  period: string
  total_revenue: number
  total_commission: number
  total_ad_spent: number
}
