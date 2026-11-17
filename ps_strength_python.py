
import tkinter as tk

# Function to check password strength
def strength(pw):
    score = 0

    if len(pw) >= 8:
        score += 1

    if any(c.isupper() for c in pw):
        score += 1

    if any(c.islower() for c in pw):
        score += 1

    if any(c.isdigit() for c in pw):
        score += 1

    if any(not c.isalnum() for c in pw):
        score += 1

    if score <= 2:
        return "Weak"

    if score <= 4:
        return "Medium"

    return "Strong"


# Colors for password strength
COLORS = {
    "Weak": "#F87171",
    "Medium": "#FBBF24",
    "Strong": "#34D399"
}


# Function to check password
def check(event=None):
    pw = entry.get()

    if pw == "" or " " in pw:
        result.config(
            text="Enter a password (no spaces)",
            fg="white"
        )
        return

    s = strength(pw)
    result.config(text=s, fg=COLORS[s])


# Function to show or hide password
def toggle():
    entry.config(
        show="" if show_var.get() else "*"
    )


# Create main window
root = tk.Tk()
root.title("Password Strength Checker")
root.geometry("380x260")
root.config(bg="#0B1F3A")


# Heading
tk.Label(
    root,
    text="Password Strength Checker",
    font=("Calibri", 16, "bold"),
    bg="#0B1F3A",
    fg="#2DD4BF"
).pack(pady=15)


# Password entry
entry = tk.Entry(
    root,
    show="*",
    font=("Calibri", 14),
    width=24
)
entry.pack(pady=5)

# Check password while typing
entry.bind("<KeyRelease>", check)


# Show password checkbox
show_var = tk.BooleanVar()

tk.Checkbutton(
    root,
    text="Show password",
    variable=show_var,
    command=toggle,
    bg="#0B1F3A",
    fg="white",
    selectcolor="#12304F",
    activebackground="#0B1F3A",
    activeforeground="white"
).pack()


# Check button
tk.Button(
    root,
    text="Check",
    font=("Calibri", 12, "bold"),
    bg="#14B8A6",
    fg="#0B1F3A",
    command=check
).pack(pady=10)


# Result label
result = tk.Label(
    root,
    text="",
    font=("Calibri", 20, "bold"),
    bg="#0B1F3A",
    fg="white"
)
result.pack()


# Run application
root.mainloop()
