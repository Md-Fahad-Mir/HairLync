const revenueData = [
  { month: "Jan", mrr: 18400, total: 22100 },
  { month: "Feb", mrr: 21200, total: 25800 },
  { month: "Mar", mrr: 19800, total: 23400 },
  { month: "Apr", mrr: 24500, total: 29700 },
  { month: "May", mrr: 27800, total: 33200 },
  { month: "Jun", mrr: 31200, total: 38500 }
];
const aiSuccessData = [
  { day: "Mon", success: 94, failed: 6 },
  { day: "Tue", success: 97, failed: 3 },
  { day: "Wed", success: 91, failed: 9 },
  { day: "Thu", success: 98, failed: 2 },
  { day: "Fri", success: 95, failed: 5 },
  { day: "Sat", success: 96, failed: 4 },
  { day: "Sun", success: 93, failed: 7 }
];
const users = [
  { id: 1, name: "Marcus Johnson", email: "marcus.j@email.com", phone: "+1 555-0101", role: "barber", verified: true, active: true, rating: 4.8, reviews: 142, bookings: 89, joined: "2024-01-15", lastActive: "2026-06-05" },
  { id: 2, name: "Sophia Chen", email: "sophia.c@email.com", phone: "+1 555-0102", role: "client", verified: false, active: true, rating: 0, reviews: 0, bookings: 23, joined: "2024-03-22", lastActive: "2026-06-04" },
  { id: 3, name: "Elite Cuts Salon", email: "info@elitecuts.com", phone: "+1 555-0103", role: "salon", verified: true, active: true, rating: 4.6, reviews: 310, bookings: 1240, joined: "2023-11-08", lastActive: "2026-06-06" },
  { id: 4, name: "Derek Williams", email: "derek.w@email.com", phone: "+1 555-0104", role: "barber", verified: false, active: false, rating: 3.9, reviews: 28, bookings: 34, joined: "2024-05-17", lastActive: "2026-05-20" },
  { id: 5, name: "Aisha Thompson", email: "aisha.t@email.com", phone: "+1 555-0105", role: "client", verified: false, active: true, rating: 0, reviews: 0, bookings: 7, joined: "2026-02-10", lastActive: "2026-06-01" },
  { id: 6, name: "The Grooming Hub", email: "admin@groomhub.com", phone: "+1 555-0106", role: "salon", verified: true, active: true, rating: 4.9, reviews: 502, bookings: 3210, joined: "2023-08-01", lastActive: "2026-06-06" },
  { id: 7, name: "Jordan Rivera", email: "jordan.r@email.com", phone: "+1 555-0107", role: "barber", verified: true, active: true, rating: 4.7, reviews: 88, bookings: 112, joined: "2024-07-03", lastActive: "2026-06-06" },
  { id: 8, name: "Nina Patel", email: "nina.p@email.com", phone: "+1 555-0108", role: "client", verified: false, active: false, rating: 0, reviews: 0, bookings: 2, joined: "2026-04-19", lastActive: "2026-04-22" }
];
const appointments = [
  { id: "APT-001", client: "Sophia Chen", provider: "Marcus Johnson", service: "Taper Fade", date: "2026-06-07", time: "10:00 AM", duration: 45, price: 35, status: "pending", description: "Classic taper fade with beard trim", cancelledBy: null, cancelReason: null },
  { id: "APT-002", client: "Aisha Thompson", provider: "Elite Cuts Salon", service: "Balayage & Blowout", date: "2026-06-06", time: "2:30 PM", duration: 120, price: 145, status: "approved", description: "Full balayage treatment with blow dry", cancelledBy: null, cancelReason: null },
  { id: "APT-003", client: "Derek Williams", provider: "Jordan Rivera", service: "Skin Fade", date: "2026-06-05", time: "11:00 AM", duration: 50, price: 40, status: "completed", description: "Low skin fade with line-up", cancelledBy: null, cancelReason: null },
  { id: "APT-004", client: "Nina Patel", provider: "The Grooming Hub", service: "Keratin Treatment", date: "2026-06-04", time: "9:00 AM", duration: 180, price: 220, status: "cancelled", description: "Full keratin smoothing treatment", cancelledBy: "client", cancelReason: "Personal emergency" },
  { id: "APT-005", client: "Marcus Johnson", provider: "Elite Cuts Salon", service: "Color & Cut", date: "2026-06-08", time: "3:00 PM", duration: 90, price: 95, status: "pending", description: "Full color treatment with precision cut", cancelledBy: null, cancelReason: null },
  { id: "APT-006", client: "Sophia Chen", provider: "Jordan Rivera", service: "Beard Sculpt", date: "2026-06-03", time: "1:00 PM", duration: 30, price: 25, status: "completed", description: "Beard shaping and detailing", cancelledBy: null, cancelReason: null }
];
const aiQueue = [
  { id: "AI-001", user: "Sophia Chen", email: "sophia.c@email.com", uploaded: "2026-06-06 09:12", status: "pending", result: null, faceShape: null },
  { id: "AI-002", user: "Aisha Thompson", email: "aisha.t@email.com", uploaded: "2026-06-06 08:45", status: "completed", result: ["Modern Textured Pompadour with Skin Fade", "Classic Taper Fade", "Curly Fringe Style"], faceShape: "Oval" },
  { id: "AI-003", user: "Derek Williams", email: "derek.w@email.com", uploaded: "2026-06-05 16:30", status: "failed", result: null, faceShape: null },
  { id: "AI-004", user: "Nina Patel", email: "nina.p@email.com", uploaded: "2026-06-05 14:20", status: "completed", result: ["Modern Quiff", "Low Fade Buzz Cut", "Classic Taper Fade"], faceShape: "Round" },
  { id: "AI-005", user: "Jordan Rivera", email: "jordan.r@email.com", uploaded: "2026-06-06 10:05", status: "processing", result: null, faceShape: null }
];
const reviews = [
  { id: "REV-001", author: "Sophia Chen", target: "Marcus Johnson", rating: 5, content: "Absolutely amazing fade! Marcus is incredibly skilled and made me feel very comfortable. Will definitely be coming back.", date: "2026-06-05", status: "approved", flagReason: null },
  { id: "REV-002", author: "Aisha Thompson", target: "Elite Cuts Salon", rating: 2, content: "Very disappointed with the service. Had to wait 45 mins past my appointment time. The stylist seemed distracted the entire time.", date: "2026-06-04", status: "flagged", flagReason: "Potentially false claim under investigation" },
  { id: "REV-003", author: "Jordan Rivera", target: "The Grooming Hub", rating: 5, content: "Best salon in the city hands down. The staff is professional, the ambiance is incredible, and the results are always perfect.", date: "2026-06-03", status: "approved", flagReason: null },
  { id: "REV-004", author: "Derek Williams", target: "Jordan Rivera", rating: 1, content: "TERRIBLE service!!! Never going back. This barber is a complete fraud and should be banned from the platform immediately!!!!", date: "2026-06-02", status: "flagged", flagReason: "Abusive language, suspected bot activity" },
  { id: "REV-005", author: "Nina Patel", target: "Marcus Johnson", rating: 4, content: "Great haircut, very clean lines. The atmosphere was relaxed and Marcus was friendly and professional throughout.", date: "2026-06-01", status: "pending", flagReason: null },
  { id: "REV-006", author: "Sophia Chen", target: "Elite Cuts Salon", rating: 5, content: "Outstanding experience! The balayage came out beautifully and the entire team was wonderful.", date: "2026-05-30", status: "approved", flagReason: null }
];
export {
  aiQueue,
  aiSuccessData,
  appointments,
  revenueData,
  reviews,
  users
};
