"""Indian first names and honorifics for synthetic transcripts."""

from __future__ import annotations

import random
from typing import Sequence

# 200+ distinct first names (Hindi/Marathi/common North+West+South mix for kirana context)
FIRST_NAMES: tuple[str, ...] = (
    "Ramesh", "Suresh", "Mahesh", "Ganesh", "Rajesh", "Dinesh", "Naresh", "Mukesh",
    "Amit", "Anil", "Sunil", "Kapil", "Rahul", "Rohit", "Ajay", "Vijay", "Sanjay",
    "Arun", "Varun", "Kiran", "Niranjan", "Prakash", "Pradeep", "Deepak", "Ashok",
    "Vinod", "Manoj", "Sanoj", "Pankaj", "Sachin", "Nitin", "Ravi", "Kavi", "Dev",
    "Kunal", "Vishal", "Sonal", "Payal", "Neha", "Rekha", "Geeta", "Seeta", "Lata",
    "Usha", "Asha", "Nisha", "Trisha", "Priya", "Divya", "Anjali", "Kavita", "Savita",
    "Sunita", "Anita", "Rita", "Mira", "Kiran", "Pooja", "Manju", "Radha", "Sudha",
    "Lakshmi", "Parvati", "Gauri", "Savitri", "Kamala", "Padma", "Shanti", "Shobha",
    "Vandana", "Archana", "Meena", "Leela", "Sheela", "Beena", "Veena", "Reena",
    "Mohit", "Rohit", "Sumit", "Amitabh", "Abhishek", "Akash", "Vikas", "Rakesh",
    "Makesh", "Hitesh", "Yogesh", "Girish", "Harish", "Satish", "Umesh", "Ganpat",
    "Shankar", "Shyam", "Ram", "Krishna", "Balram", "Hanuman", "Bharat", "Suraj",
    "Chand", "Chandra", "Devendra", "Rajendra", "Mahendra", "Surendra", "Gopal",
    "Mohan", "Sohan", "Rohan", "Kishan", "Kisan", "Baburao", "Tukaram", "Vitthal",
    "Pandurang", "Dattatray", "Narayan", "Laxman", "Eknath", "Namdev", "Santosh",
    "Rameshwar", "Shivaji", "Bajirao", "Sambhaji", "Rajaram", "Tanaji", "Kondiba",
    "Bhau", "Anna", "Dada", "Tai", "Kaka", "Mama", "Mousi", "Bhabhi", "Bhaiya",
    "Sharma", "Patil", "Desai", "Jadhav", "Kulkarni", "Pawar", "More", "Shinde",
    "Gaikwad", "Chavan", "Thakur", "Yadav", "Singh", "Kumar", "Gupta", "Verma",
    "Reddy", "Naidu", "Iyer", "Menon", "Nair", "Pillai", "Shah", "Mehta", "Jain",
    "Agarwal", "Bansal", "Malhotra", "Khanna", "Kapoor", "Chopra", "Bhatia", "Sethi",
    "Farhan", "Imran", "Salim", "Rahim", "Karim", "Ayesha", "Fatima", "Zarina",
    "Nasreen", "Parveen", "Sabeena", "Rafiq", "Shabbir", "Iqbal", "Hamid", "Khalid",
    "Joseph", "Thomas", "George", "Antony", "Francis", "Mary", "Rosy", "Sunny",
    "Bobby", "Vicky", "Ricky", "Monty", "Sonu", "Monu", "Guddu", "Pappu", "Chintu",
    "Bunty", "Mintu", "Raju", "Babu", "Chotu", "Golu", "Munna", "Pintu", "Lalu",
    "Kalpana", "Sarika", "Swati", "Shruti", "Smriti", "Preeti", "Priti", "Arti",
    "Bhavna", "Chhaya", "Durga", "Ganga", "Jamuna", "Kaveri", "Narmada", "Saraswati",
    "Tara", "Uma", "Vimala", "Yamuna", "Zoya", "Aarav", "Vihaan", "Advait", "Ishaan",
    "Kabir", "Arjun", "Kartik", "Dhruv", "Shaurya", "Aryan", "Vivaan", "Reyansh",
    "Myra", "Aanya", "Diya", "Kiara", "Saanvi", "Anaya", "Ira", "Mira", "Navya",
    "Pranav", "Tejas", "Omkar", "Siddharth", "Harsh", "Yash", "Aditya", "Kartik",
    "Nikhil", "Sahil", "Tarun", "Varun", "Karan", "Arman", "Fardeen", "Zain",
    "Bulbul", "Chameli", "Gulab", "Kamal", "Motilal", "Hiralal", "Ramprasad", "Shyamlal",
    "Gangaram", "Kishanlal", "Manilal", "Jethalal", "Champak", "Popatlal", "Iyer",
    "Subramanian", "Krishnan", "Raman", "Murugan", "Selvam", "Velu", "Pandian",
)

HONORIFICS: tuple[str, ...] = (
    "ji",
    "bhai",
    "bhau",
    "tai",
    "kaka",
    "aaji",
    "uncle",
    "didi",
    "ben",
    "saheb",
    "madam",
    "sir",
)

# ASR-style spelling variants for same phonetic name
NAME_VARIANTS: dict[str, tuple[str, ...]] = {
    "Ramesh": ("Rmesh", "Ramish", "Rames"),
    "Suresh": ("Surish", "Sureshh"),
    "Mahesh": ("Mhesh", "Maheshh"),
    "Ganesh": ("Ganish", "Ganes"),
    "Sharma": ("Sharmaa", "Sarma"),
    "Patil": ("Paatil", "Patel"),
    "Prakash": ("Prkash", "Parakash"),
    "Lakshmi": ("Laxmi", "Laksmi"),
    "Kulkarni": ("Kulkani", "Kulakarni"),
    "Jadhav": ("Jadhao", "Jadhav"),
}


def format_customer_name(
    rng: random.Random,
    first: str,
    *,
    use_honorific: bool = True,
    use_surname: bool = False,
    surname_pool: Sequence[str] | None = None,
) -> str:
    """Build display name like 'Ramesh ji' or 'Sharma bhai'."""
    pool = surname_pool or ("Sharma", "Patil", "Yadav", "Singh", "Desai", "Kulkarni")
    if use_surname and rng.random() < 0.35:
        base = rng.choice(pool)
        hon = rng.choice(HONORIFICS[:6])
        return f"{base} {hon}"
    hon = rng.choice(HONORIFICS) if use_honorific else ""
    if hon:
        return f"{first} {hon}".strip()
    return first


def maybe_variant_name(rng: random.Random, name: str) -> str:
    if name in NAME_VARIANTS and rng.random() < 0.2:
        return rng.choice(NAME_VARIANTS[name])
    return name


def split_train_test_names(seed: int) -> tuple[set[str], set[str]]:
    """Hold out ~30% of unique first names for generalisation test."""
    rng = random.Random(seed)
    names = list(FIRST_NAMES)
    rng.shuffle(names)
    n_hold = max(60, len(names) // 3)
    held = set(names[:n_hold])
    train_names = set(names[n_hold:])
    return train_names, held
