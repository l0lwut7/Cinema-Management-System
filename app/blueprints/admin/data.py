VIP_SPENDERS = [
    {"initials": "JD", "color": "amber", "name": "John Davidson", "email": "john.d@email.com", "tier": "Gold", "tier_color": "amber", "spent": "$2,450", "visits": 18, "avg": "$136.11"},
    {"initials": "SM", "color": "slate-400", "name": "Sarah Mitchell", "email": "sarah.m@email.com", "tier": "Platinum", "tier_color": "slate-400", "spent": "$1,890", "visits": 14, "avg": "$135.00"},
    {"initials": "MR", "color": "amber", "name": "Michael Roberts", "email": "m.roberts@email.com", "tier": "Gold", "tier_color": "amber", "spent": "$1,675", "visits": 12, "avg": "$139.58"},
    {"initials": "EW", "color": "sky", "name": "Emily Watson", "email": "emily.w@email.com", "tier": "Silver", "tier_color": "sky", "spent": "$1,420", "visits": 11, "avg": "$129.09"}
]

EMPLOYEES = [
    {"initials": "JW", "color": "emerald", "name": "James Wilson", "role": "Theater Manager", "auth_level": "Admin", "auth_color": "crimson", "salary": "$65,000"},
    {"initials": "RC", "color": "amber", "name": "Rachel Chen", "role": "Senior Cashier", "auth_level": "Moderator", "auth_color": "amber", "salary": "$42,000"},
    {"initials": "TB", "color": "sky", "name": "Tom Brown", "role": "Projectionist", "auth_level": "Staff", "auth_color": "slate-600", "salary": "$38,000"},
    {"initials": "NH", "color": "crimson", "name": "Nancy Hall", "role": "Concession Lead", "auth_level": "Staff", "auth_color": "slate-600", "salary": "$35,000"}
]

MOVIES = [
    {"name": "Galactic Odyssey", "genres": [("Sci-Fi", "crimson"), ("Action", "sky")], "duration": "148 min"},
    {"name": "Midnight Whispers", "genres": [("Horror", "amber"), ("Thriller", "emerald")], "duration": "118 min"},
    {"name": "Love in Paris", "genres": [("Romance", "crimson"), ("Comedy", "sky")], "duration": "105 min"},
    {"name": "The Last Stand", "genres": [("Action", "sky"), ("Drama", "emerald")], "duration": "134 min"}
]

UPCOMING_SCREENINGS = [
    {"movie": "Galactic Odyssey", "status": "Active", "status_color": "emerald", "saloon": "Saloon A", "time": "Today, 14:30", "price": "$18.00"},
    {"movie": "Midnight Whispers", "status": "Active", "status_color": "emerald", "saloon": "Saloon B", "time": "Today, 19:00", "price": "$15.00"},
    {"movie": "The Last Stand", "status": "Scheduled", "status_color": "sky", "saloon": "Saloon C (IMAX)", "time": "Tomorrow, 20:30", "price": "$22.00"}
]

SALOONS = [
    {"name": "Saloon A", "info": "120 seats • Standard", "status": "Active", "status_color": "emerald"},
    {"name": "Saloon B", "info": "85 seats • Standard", "status": "Active", "status_color": "emerald"},
    {"name": "Saloon C", "info": "200 seats • IMAX", "status": "Active", "status_color": "emerald"},
    {"name": "Saloon D", "info": "60 seats • VIP", "status": "Maintenance", "status_color": "amber"}
]

CONSUMABLES = [
    {"name": "Popcorn (Large)", "price": "$8.50", "stock": "Stock: 245 units", "stock_class": "text-slate-400", "wrapper_class": ""},
    {"name": "Coca-Cola (Med)", "price": "$5.00", "stock": "Stock: 180 units", "stock_class": "text-slate-400", "wrapper_class": ""},
    {"name": "Nachos", "price": "$7.00", "stock": "Stock: 12 units ⚠️", "stock_class": "text-amber", "wrapper_class": "border border-amber/30"},
    {"name": "Hot Dog", "price": "$6.50", "stock": "Stock: 95 units", "stock_class": "text-slate-400", "wrapper_class": ""}
]

DEALS = [
    {"name": "Movie + Popcorn Combo", "status": "Active", "status_color": "emerald", "desc": "Save $5 on ticket + large popcorn", "valid": "Valid: Jan 1 - Mar 31"},
    {"name": "Family Pack", "status": "Active", "status_color": "emerald", "desc": "4 tickets + 2 popcorns + 4 drinks", "valid": "Valid: Weekends only"},
    {"name": "Early Bird Special", "status": "Inactive", "status_color": "slate-600", "desc": "20% off shows before 12pm", "valid": "Expired: Dec 31"}
]

VIP_TIER = {
    "name": "VIP Member", 
    "color": "amber", 
    "border": "border-amber", 
    "spend": "$500 Annual Spend", 
    "discount": "15% off tickets & snacks", 
    "points": "2x Points on all purchases"
}

GENRES = ["Action", "Comedy", "Drama", "Horror", "Sci-Fi", "Thriller", "Romance", "Animation", "Documentary"]

FORMATS = ["2D", "3D", "IMAX", "4DX"]
