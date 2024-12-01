from nicegui import ui
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from music21 import *
import os

console = Console()

def accidental_to_str(a: str, proper_flat: bool = False) -> str:
    """
    Converts an accidental of the form ["Natural(♮)", "Sharp(#)", "Flat(♭)"] to a string of the form ["", "#", "-"] respectively.
    """
    match a:
        case "Natural(♮)":
            return ""
        
        case "Sharp(#)":
            return "#"
        
        case "Flat(♭)":
            if proper_flat:
                return "♭"
            else:
                return "-"

        case _:
            return ""

def build_chord(
        root: note.Note, # The root note
        type: str = "major", # options: (major, minor, dim, aug, dominant)
        suspended: int = 0, # 0 means that the major/minor third will not be changed
        extended: int = 5, # extends chords up to a 13th. Default is 5, which means a normal triad
        alter: tuple[str, int] = ("", 0), # Alters a note in the chord. The string indicates a flat or sharp, and the number indicates the note.
        add: int = 0, # Add a note to the chord(e.g. add9 add13)
) -> chord.Chord:
    ch_key = key.Key(root.pitch)
    ch: list[note.Note] = [root]

    # Building the structure of the chord based
    match type:
        case "dominant":
            ch.append(root.transpose(4)) # major 3rd
            ch.append(root.transpose(7)) # perfect 5th
            ch.append(root.transpose(10)) # flat 7th
        
        case "major":
            ch.append(root.transpose(4)) # major 3rd
            ch.append(root.transpose(7)) # perfect 5th

        case "minor":
            ch.append(root.transpose(3)) # minor 3rd
            ch.append(root.transpose(7)) # perfect 5th
        
        case "dim":
            ch.append(root.transpose(3)) # minor 3rd
            ch.append(root.transpose(6)) # diminished 5th
        
        case "aug":
            ch.append(root.transpose(4)) # major 3rd
            ch.append(root.transpose(8)) # augmented 5th

    # Suspended notes
    match suspended:
        case 0:
            pass

        case 2:
            ch[1] = root.transpose(2)

        case 4:
            ch[1] = root.transpose(5)

        case _:
            pass
    
    # Extend chord up to a 9th, 11th, etc
    if extended != 5:
        current_note = 7
        while current_note <= extended:
            ch.append(root.transpose(interval.GenericInterval(current_note)))
            current_note += 2

    # Add notes
    if add != 0:
        ch.append(root.transpose(interval.GenericInterval(add)))

    # Altering specific notes
    if alter != ("", 0):
        ch[int((alter[1] - 1) / 2)].pitch.accidental = alter[0]

    return chord.Chord(ch)

def name_chord(
    root: str,
    root_accidental: str,
    type: str,
    sus: str,
    size: str,
    alter: str | int,
    alter_accidental: str,
    add: str | int,
    only_chord_name: bool = False,
):
    chord_name = ""
    chord_name += f"{root}{accidental_to_str(root_accidental, True)}"
    chord_parts = {
        "root": note.Note(f"{root}{accidental_to_str(root_accidental)}"),
        "type": "major",
        "suspended": 0,
        "extended": 5,
        "alter": ("", 0),
        "add": 0
    }

    match type:
        case "Major":
            chord_name += "maj"
            chord_parts["type"] = "major"
        
        case "Minor":
            chord_name += "m"
            chord_parts["type"] = "minor"

        case "Dominant":
            # Add nothing to the name
            chord_parts["type"] = "dominant"
        
        case "Augmented":
            chord_name += "+"
            chord_parts["type"] = "aug"

        case "Diminished":
            chord_name += "dim"
            chord_parts["type"] = "dim"

    if size == "Triad":
        chord_parts["extended"] = 5
    else:
        chord_name += size[0:-2]
        chord_parts["extended"] = int(size[0: -2])

    if sus != "No sus":
        chord_name += sus
        chord_parts["suspended"] = int(sus[-1])
    else:
        chord_parts["suspended"] = 0
    
    if add != "None":
        chord_name += f"add{add}"
        chord_parts["add"] = add

    if alter != "None":
        chord_name += f"({alter_accidental[-2]}{alter})"
        chord_parts["alter"] = (alter_accidental[0:-3], alter)
    
    if only_chord_name:
        return chord_name
    else:
        built_chord = build_chord(
            chord_parts["root"],
            chord_parts["type"],
            chord_parts["suspended"],
            chord_parts["extended"],
            chord_parts["alter"],
            chord_parts["add"],
        )
        return (chord_name, built_chord)

def main():
    def inject_data():
        with ui.teleport(chord_data_placeholder):
            if None in [ch_root_note.value,
                ch_root_accidental.value,
                ch_type.value,
                ch_sus.value,
                ch_size.value,
                ch_alter_note.value,
                ch_alter_accidental.value,
                ch_add]: return
            ch_name, ch_notes = name_chord(
                ch_root_note.value,
                ch_root_accidental.value,
                ch_type.value,
                ch_sus.value,
                ch_size.value,
                ch_alter_note.value,
                ch_alter_accidental.value,
                ch_add.value,
            )
            ui.label("Chord name").style("font-size: 125%").classes("w-full")
            ui.label(ch_name).classes("w-full")
            ui.label("Chord notes").style("font-size: 125%").classes("w-full")
            ui.label(", ".join(x.name for x in ch_notes.pitches)).classes("w-full")
            ui.separator()

    with ui.row().classes("justify-center w-full"):
        with ui.card().classes("col-6"):
            ui.label("Chord Generator").style("font-size: 200%; font-weight: 500")
            with ui.row().classes("w-full justify-center"):
                with ui.row().classes("col-5"):
                    ui.label("Inputs").style("font-size: 150%;").classes("col-12")

                    ui.label("Root Note")
                    ch_root_note = ui.select(
                        options=["A", "B", "C", "D", "E", "F", "G",],
                        label="Root note",
                        value="C",
                    ).classes("col-12")
                    ch_root_accidental = ui.radio(["Natural(♮)", "Sharp(#)", "Flat(♭)"], value="Natural(♮)").props("inline").classes("col-12").style("font-size: 99%")

                    ui.separator()

                    ui.label("Chord Type")
                    ch_type = ui.select(
                        options=["Major", "Minor", "Dominant", "Diminished", "Augmented"],
                        label="Chord Type",
                        value="Major",
                    ).classes("col-12")

                    ui.separator()

                    ui.label("Suspended Notes")
                    ch_sus = ui.radio(["No sus", "sus2", "sus4"], value="No sus").props("inline").classes("col-12").style("font-size: 100%")

                    ui.separator()

                    ui.label("Chord Size")
                    ch_size = ui.select(
                        options=["Triad", "7th", "9th", "11th", "13th"],
                        label="Chord size",
                        value="Triad",
                    ).classes("col-12")

                    ui.separator()

                    ui.label("Altered notes").classes("col-12")
                    ch_alter_note = ui.select(
                        options=["None", 1, 3, 5, 7, 9, 11, 13],
                        label="Altered note",
                        value="None",
                    ).classes("col-5")
                    ch_alter_accidental = ui.select(
                        options=["Natural(♮)", "Sharp(#)", "Flat(♭)"],
                        label="Accidental",
                        value="Natural(♮)",
                    ).classes("col-6")

                    ui.separator()

                    ui.label("Added notes")
                    ch_add = ui.select(
                        options=["None", 9, 11, 13],
                        label="Added note",
                        value="None",
                    ).classes("col-12")
                with ui.row().classes("col-6"):
                    ui.label("History").classes("col-12").style("font-size: 150%")
                    ui.separator()
                    chord_data_placeholder = ui.row().classes("w-full")
                    ui.button("Generate Chord", on_click=inject_data).classes("col-12")
    
    ui.run()

main()