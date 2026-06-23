"""
Scene panel — center panel for configuring and resolving a scene.
"""
import uuid
import customtkinter as ctk
from pta_manager.models.scene import Scene
from pta_manager.services.card_service import is_red
from pta_manager.services.dice_service import roll_dice
from pta_manager.services.resolution_service import resolve_cards, resolve_dice
from pta_manager.ui.app_state import AppState


class ScenePanel(ctk.CTkFrame):
    """Scene creation and resolution panel with participant and resolve columns."""

    def __init__(self, parent, state: AppState, on_resolve, on_state_change, **kwargs):
        super().__init__(parent, **kwargs)
        self._state = state
        self._on_resolve = on_resolve
        self._on_state_change = on_state_change
        self._scene_type = ctk.StringVar(value="C")
        self._producer_spend = ctk.IntVar(value=0)
        self._participant_vars: dict[str, ctk.BooleanVar] = {}
        self._fan_mail_vars: dict[str, ctk.IntVar] = {}
        self._trait_count_vars: dict[str, ctk.IntVar] = {}  # trait count, not toggle

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build()
        self.refresh()

    def _build(self):
        self._panel_label = ctk.CTkLabel(self, text="Scene Panel", font=ctk.CTkFont(size=14, weight="bold"))
        self._panel_label.grid(row=0, column=0, columnspan=2, padx=8, pady=8, sticky="w")

        form = ctk.CTkFrame(self)
        form.grid(row=1, column=0, columnspan=2, sticky="ew", padx=8, pady=(0, 8))
        form.grid_columnconfigure(1, weight=1)
        form.grid_columnconfigure(3, weight=0)

        ctk.CTkLabel(form, text="Title").grid(row=0, column=0, padx=8, pady=4, sticky="w")
        self._title_entry = ctk.CTkEntry(form, placeholder_text="Scene title")
        self._title_entry.grid(row=0, column=1, padx=8, pady=4, sticky="ew")

        ctk.CTkLabel(form, text="Type").grid(row=0, column=2, padx=(16, 8), pady=4, sticky="w")
        self._type_combo = ctk.CTkComboBox(
            form,
            values=["C", "P"],
            variable=self._scene_type,
            state="readonly",
            width=50,
        )
        self._type_combo.set("C")
        self._type_combo.grid(row=0, column=3, padx=(0, 8), pady=4, sticky="w")

        ctk.CTkLabel(self, text="Participants").grid(row=2, column=0, padx=8, pady=(0, 4), sticky="w")
        self._participants_frame = ctk.CTkScrollableFrame(self)
        self._participants_frame.grid(row=3, column=0, sticky="nsew", padx=(8, 4), pady=(0, 8))
        self._participants_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="Traits & Fan Mail Spend").grid(row=2, column=1, padx=8, pady=(0, 4), sticky="w")
        self._trait_panel = ctk.CTkScrollableFrame(self)
        self._trait_panel.grid(row=3, column=1, sticky="nsew", padx=(4, 8), pady=(0, 8))
        self._trait_panel.grid_columnconfigure(0, weight=1)

        self._resolve_row = ctk.CTkFrame(self)
        self._resolve_row.grid(row=4, column=0, columnspan=2, sticky="ew", padx=8, pady=(0, 8))
        self._resolve_row.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(self._resolve_row, text="Producer spend this scene:").grid(
            row=0, column=0, padx=(8, 6), pady=8, sticky="w"
        )
        ctk.CTkButton(self._resolve_row, text="-", width=28, command=lambda: self._change_producer_spend(-1)).grid(
            row=0, column=1, padx=2, pady=8
        )
        self._producer_spend_label = ctk.CTkLabel(self._resolve_row, textvariable=self._producer_spend, width=30)
        self._producer_spend_label.grid(row=0, column=2, padx=2, pady=8)
        ctk.CTkButton(self._resolve_row, text="+", width=28, command=lambda: self._change_producer_spend(1)).grid(
            row=0, column=3, padx=2, pady=8, sticky="w"
        )
        ctk.CTkButton(self._resolve_row, text="Resolve Scene", command=self._resolve_scene).grid(
            row=0, column=4, padx=(8, 8), pady=8, sticky="e"
        )

    def _update_panel_label(self):
        scene_number = self._state.episode_info.get("scene", 0)
        mode = self._state.mode
        cards_left = self._state.deck.remaining if self._state.mode == "CARD_MODE" else "—"
        label_text = f"Scene #{scene_number} | Budget: {self._state.producer_budget} | Mode: {mode}"
        self._panel_label.configure(text=label_text)

    def _sync_participants_ui(self):
        for widget in self._participants_frame.winfo_children():
            widget.destroy()

        self._participant_vars = {}
        ctk.CTkLabel(
            self._participants_frame,
            text=f"Producer budget: {self._state.producer_budget} (always in scene)",
            font=ctk.CTkFont(weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=6, pady=(4, 8))

        scene_number = self._state.episode_info.get("scene", 0) + 1
        for row, protagonist in enumerate(self._state.protagonists, start=1):
            var = ctk.BooleanVar(value=True)
            self._participant_vars[protagonist.id] = var
            scene_sp = protagonist.get_screen_presence_for_scene(scene_number)
            ctk.CTkCheckBox(
                self._participants_frame,
                text=f"{protagonist.name} (SP {scene_sp}, FM {protagonist.fan_mail})",
                variable=var,
                command=self._sync_trait_panel,
            ).grid(row=row, column=0, sticky="w", padx=6, pady=3)

    def _sync_trait_panel(self):
        for widget in self._trait_panel.winfo_children():
            widget.destroy()

        self._fan_mail_vars = {}
        self._trait_count_vars = {}
        row = 0
        for protagonist in self._state.protagonists:
            selected = self._participant_vars.get(protagonist.id)
            if selected is None or not selected.get():
                continue

            ctk.CTkLabel(
                self._trait_panel,
                text=protagonist.name,
                font=ctk.CTkFont(weight="bold"),
            ).grid(row=row, column=0, padx=6, pady=(4, 2), sticky="w")
            row += 1

            scene_number = self._state.episode_info.get("scene", 0) + 1
            scene_sp = protagonist.get_screen_presence_for_scene(scene_number)

            trait_count_var = ctk.IntVar(value=0)
            self._trait_count_vars[protagonist.id] = trait_count_var
            trait_row = ctk.CTkFrame(self._trait_panel, fg_color="transparent")
            trait_row.grid(row=row, column=0, padx=16, pady=2, sticky="w")
            ctk.CTkLabel(trait_row, text=f"Traits (max {scene_sp}):").grid(row=0, column=0, padx=(0, 6), sticky="w")
            ctk.CTkButton(
                trait_row,
                text="-",
                width=28,
                command=lambda pid=protagonist.id, sp=scene_sp: self._change_trait_count(pid, -1, sp),
            ).grid(row=0, column=1, padx=2)
            ctk.CTkLabel(trait_row, textvariable=trait_count_var, width=30).grid(row=0, column=2, padx=2)
            ctk.CTkButton(
                trait_row,
                text="+",
                width=28,
                command=lambda pid=protagonist.id, sp=scene_sp: self._change_trait_count(pid, 1, sp),
            ).grid(row=0, column=3, padx=2)
            row += 1

            fm_var = ctk.IntVar(value=0)
            self._fan_mail_vars[protagonist.id] = fm_var
            fm_row = ctk.CTkFrame(self._trait_panel, fg_color="transparent")
            fm_row.grid(row=row, column=0, padx=16, pady=(0, 6), sticky="w")
            ctk.CTkLabel(fm_row, text="Fan Mail spend:").grid(row=0, column=0, padx=(0, 6), sticky="w")
            ctk.CTkButton(
                fm_row,
                text="-",
                width=28,
                command=lambda pid=protagonist.id: self._change_fan_mail(pid, -1),
            ).grid(row=0, column=1, padx=2)
            ctk.CTkLabel(fm_row, textvariable=fm_var, width=30).grid(row=0, column=2, padx=2)
            ctk.CTkButton(
                fm_row,
                text="+",
                width=28,
                command=lambda pid=protagonist.id: self._change_fan_mail(pid, 1),
            ).grid(row=0, column=3, padx=2)
            row += 1

    def _change_trait_count(self, protagonist_id: str, delta: int, max_sp: int):
        var = self._trait_count_vars.get(protagonist_id)
        if var is None:
            return
        new_value = max(0, min(max_sp, var.get() + delta))
        var.set(new_value)

    def _change_fan_mail(self, protagonist_id: str, delta: int):
        protagonist = next((p for p in self._state.protagonists if p.id == protagonist_id), None)
        if protagonist is None:
            return
        var = self._fan_mail_vars.get(protagonist_id)
        if var is None:
            return
        new_value = max(0, min(protagonist.fan_mail, var.get() + delta))
        var.set(new_value)

    def _change_producer_spend(self, delta: int):
        current = self._producer_spend.get()
        max_spend = min(5, self._state.producer_budget)
        self._producer_spend.set(max(0, min(max_spend, current + delta)))

    def _build_confirmation_text(self, participant_ids: list[str], producer_spend: int) -> str:
        lines = [
            "Resolve this scene?",
            "",
            f"Mode: {self._state.mode}",
            f"Producer spend: {producer_spend}",
            "",
            "Participants & Dice/Cards:",
        ]
        scene_number = self._state.episode_info.get("scene", 0) + 1
        for protagonist in [p for p in self._state.protagonists if p.id in participant_ids]:
            scene_sp = protagonist.get_screen_presence_for_scene(scene_number)
            traits_used = self._trait_count_vars.get(protagonist.id, ctk.IntVar(value=0)).get()
            fm_spend = self._fan_mail_vars.get(protagonist.id, ctk.IntVar(value=0)).get()
            total_dice = scene_sp + traits_used + fm_spend
            lines.append(f"- {protagonist.name}: {total_dice} total (SP {scene_sp} + {traits_used} traits + {fm_spend} fan mail)")
        lines.append("")
        lines.append("Choose Yes to roll/draw now.")
        return "\n".join(lines)

    def _resolve_scene(self):
        title = self._title_entry.get().strip() or "Untitled Scene"
        scene_type = "character" if self._scene_type.get() == "C" else "plot"
        participant_ids = [pid for pid, var in self._participant_vars.items() if var.get()]

        if not participant_ids:
            self._on_resolve("No participants selected.")
            return

        producer_spend = self._producer_spend.get()
        producer_dice_count = min(1 + producer_spend, 6)

        confirmation_text = self._build_confirmation_text(participant_ids, producer_spend)
        from tkinter import messagebox
        confirmed = messagebox.askyesno("Confirm Scene Resolve", confirmation_text)
        if not confirmed:
            self._on_resolve("Scene resolve canceled.")
            return

        scene = Scene(
            id=str(uuid.uuid4()),
            title=title,
            scene_type=scene_type,
            question="",  # no longer used; each protagonist has their own context
            participant_ids=participant_ids,
            producer_budget_spent=producer_spend,
        )

        self._on_resolve(f"\n=== Scene: {title} | Type: {scene_type.upper()} ===")

        scene_number = self._state.episode_info.get("scene", 0) + 1
        producer_fan_mail_earned = 0

        for protagonist in [p for p in self._state.protagonists if p.id in participant_ids]:
            scene_sp = protagonist.get_screen_presence_for_scene(scene_number)
            traits_used = self._trait_count_vars.get(protagonist.id, ctk.IntVar(value=0)).get()
            fm_spend = self._fan_mail_vars.get(protagonist.id, ctk.IntVar(value=0)).get()
            total_dice = scene_sp + traits_used + fm_spend

            if self._state.mode == "DICE_MODE":
                protagonist_rolls = roll_dice(total_dice, "mixed")
                producer_rolls = roll_dice(producer_dice_count, "producer")
                result = resolve_dice(protagonist.id, protagonist_rolls, producer_rolls)

                # Count producer fan mail from fan mail dice rolls
                for die in protagonist_rolls:
                    if fm_spend > 0 and die.value % 2 == 0:
                        producer_fan_mail_earned += 1
                        fm_spend -= 1

                p_values = [d.value for d in protagonist_rolls]
                prod_values = [d.value for d in producer_rolls]
                self._on_resolve(
                    f"  {protagonist.name}: {p_values} vs Producer {prod_values} => {result.outcome}"
                )
            else:
                protagonist_cards = self._state.deck.draw(total_dice)
                producer_cards = self._state.deck.draw(producer_dice_count)
                result = resolve_cards(protagonist.id, protagonist_cards, producer_cards)

                # Count producer fan mail from fan mail card draws
                red_fm_cards = sum(
                    1
                    for card in protagonist_cards[-fm_spend:] if fm_spend > 0
                    if is_red(card)
                )
                producer_fan_mail_earned += red_fm_cards

                p_cards = [f"{c['rank']}-{c['suit'][0].upper()}" for c in protagonist_cards]
                prod_cards = [f"{c['rank']}-{c['suit'][0].upper()}" for c in producer_cards]
                self._on_resolve(
                    f"  {protagonist.name}: {p_cards} vs Producer {prod_cards} => {result.outcome}"
                )

            scene.results[protagonist.id] = result
            protagonist.fan_mail = max(0, protagonist.fan_mail - fm_spend)

        self._state.producer_budget = max(0, self._state.producer_budget - producer_spend)
        self._state.audience_pool += producer_fan_mail_earned
        self._state.scenes.append(scene)
        self._state.current_scene_id = scene.id
        self._producer_spend.set(0)

        if "scene" not in self._state.episode_info:
            self._state.episode_info["scene"] = 0
        self._state.episode_info["scene"] += 1

        self._on_resolve(f"  Producer earned {producer_fan_mail_earned} fan mail (pool now: {self._state.audience_pool})")
        self._on_resolve("")

        self._on_state_change()

    def refresh(self):
        self._update_panel_label()
        self._sync_participants_ui()
        self._sync_trait_panel()
