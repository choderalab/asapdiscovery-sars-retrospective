# Define custom colors
cmd.set_color("custom_grey", [0.7, 0.7, 0.7])  # RGB values between 0-1
cmd.set_color("custom_blue", [0.0, 0.4, 0.8])

# Get list of objects with "RMSD" prefix
molecules = [obj for obj in cmd.get_object_list() if obj.startswith("RMSD")]

# Set view and display settings
cmd.bg_color("white")
cmd.set("ray_opaque_background", "off")

ref = "215"

# Check if reference exists
if ref not in cmd.get_object_list():
    print(f"Error: Reference object '{ref}' not found")
    exit()

for mol in molecules:
    cmd.hide("everything")
    cmd.show("sticks", mol)
    cmd.show("sticks", ref)

    # Color by element
    cmd.util.cbaw(ref)  # Color by element with white carbons
    cmd.color("custom_grey", f"{ref} and elem C")  # Change carbons to cyan

    cmd.util.cbaw(mol)  # Color by element with white carbons
    cmd.color("custom_blue", f"{mol} and elem C")  # Change carbons to magenta

    cmd.viewport(600, 600)
    cmd.center(mol)
    cmd.zoom("all", complete=1)
    cmd.ray()
    cmd.png(f"comparison_{mol}.png")
