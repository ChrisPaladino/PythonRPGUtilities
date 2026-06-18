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
    """Scene creation and resolution panel."""

    def __init__(self, parent, state: AppState, on_resolve, get_producer_spend, on_state_change, **kwargs):
        super().__init__(parent, **kwargs)
        self._state = state
        self._on_resolve = on_resolve
        self._get_producer_spend = get_producer_spend
        self._on_state_change = on_state_change
        self._scene_type = ctk.StringVar(value="character")
        self._participant_vars: dict[str, ctk.BooleanVar] = {}
        self._fan_mail_vars: dict[str, ctk.IntVar] = {}
        self._trait_vars: dict[tuple[str, int], ctk.BooleanVar] = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)

        self._build()
        self.refresh()

    def _build(self):
        ctk.CTkLabel(self, text="Scene Panel", font=ctk.CTkFont(size=14, weight="bold")).grid(
            row=0, column=0, padx=8, pady=8, sticky="w"
        )

        form = ctk.CTkFrame(self)
        form.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 8))
        form.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(form, text="Title").grid(row=0, column=0, padx=8, pady=4, sticky="w")
        self._title_entry = ctk.CTkEntry(form, placeholder_text="Scene title")
        self._title_entry.grid(row=0, column=1, padx=8, pady=4, sticky="ew")

        ctk.CTkLabel(form, text="Type").grid(row=1, column=0, padx=8, pady=4, sticky="w")
        ctk.CTkSegmentedButton(
            form,
            values=["character", "plot"],
            variable=self._scene_type,
        ).grid(row=1, column=1, padx=8, pady=4, sticky="ew")

        ctk.CTkLabel(form, text="Question").grid(row=2, column=0, padx=8, pady=4, sticky="w")
        self._question_entry = ctk.CTkEntry(form, placeholder_text="Will the protagonist ...?")
        self._question_entry.grid(row=2, column=1, padx=8, pady=4, sticky="ew")

        ctk.CTkLabel(self, text="Participants").grid(row=2, column=0, padx=8, pady=(0, 4), sticky="w")
        self._participants_frame = ctk.CTkScrollableFrame(self, height=120)
        self._participants_frame.grid(row=3, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self._participants_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="Trait Toggles + Fan Mail Spend").grid(row=4, column=0, padx=8, pady=(0, 4), sticky="w")
        self._trait_panel = ctk.CTkScrollableFrame(self, height=140)
        self._trait_panel.grid(row=5, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self._trait_panel.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(self, text="Resolve Scene", command=self._resolve_scene).grid(
            row=6, column=0, padx=8, pady=(0, 8), sticky="ew"
        )

    def _sync_participants_ui(self):
        for widget in self._participants_frame.winfo_children():
            widget.destroy()

        self._participant_vars = {}
        scene_number = self._state.episode_info.get("scene", 0) + 1
        for row, protagonist in enumerate(self._state.protagonists):
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
        self._trait_vars = {}
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

            for trait_index, trait in enumerate(protagonist.traits):
                var = ctk.BooleanVar(value=False)
                self._trait_vars[(protagonist.id, trait_index)] = var
                ctk.CTkCheckBox(
                    self._trait_panel,
                    text=f"Use {trait.type}: {trait.name}",
                    variable=var,
                ).grid(row=row, column=0, padx=16, pady=2, sticky="w")
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

    def _change_fan_mail(self, protagonist_id: str, delta: int):
        protagonist = next((p for p in self._state.protagonists if p.id == protagonist_id), None)
        if protagonist is None:
            return
        var = self._fan_mail_vars[protagonist_id]
        new_value = max(0, min(protagonist.fan_mail, var.get() + delta))
        var.set(new_value)

    def _resolve_scene(self):
        title = self._title_entry.get().strip() or "Untitled Scene"
        question = self._question_entry.get().strip()
        scene_type = self._scene_type.get()
        participant_ids = [pid for pid, var in self._participant_vars.items() if var.get()]

        if not participant_ids:
            self._on_resolve("No participants selected.")
            return

        producer_spend = self._get_producer_spend()
        producer_dice_count = min(1 + producer_spend, 6)

        scene = Scene(
            id=str(uuid.uuid4()),
            title=title,
            scene_type=scene_type,
            question=question,
            participant_ids=participant_ids,
            producer_budget_spent=producer_spend,
        )

        self._on_resolve(f"Scene: {title} | Type: {scene_type}")
        self._on_resolve(f"Question: {question}")

        scene_number = self._state.episode_info.get("scene", 0) + 1

        for protagonist in [p for p in self._state.protagonists if p.id in participant_ids]:
            scene_sp = protagonist.get_screen_presence_for_scene(scene_number)
            used_traits = sum(
                1
                for trait_index, _ in enumerate(protagonist.traits)
                if self._trait_vars.get((protagonist.id, trait_index), ctk.BooleanVar(value=False)).get()
            )
            fm_spend = self._fan_mail_vars.get(protagonist.id, ctk.IntVar(value=0)).get()
            total_dice = scene_sp + used_traits + fm_spend

            if self._state.mode == "DICE_MODE":
                protagonist_rolls = []
                protagonist_rolls.extend(roll_dice(scene_sp, "screen_presence"))
                if used_traits:
                    protagonist_rolls.extend(roll_dice(used_traits, "trait"))
                if fm_spend:
                    protagonist_rolls.extend(roll_dice(fm_spend, "fan_mail"))

                producer_rolls = roll_dice(producer_dice_count, "producer_budget")
                result = resolve_dice(protagonist.id, protagonist_rolls, producer_rolls)

                for die in protagonist_rolls:
                    if die.source == "fan_mail" and die.value % 2 == 0:
                        self._state.producer_budget += 1

                p_values = [d.value for d in protagonist_rolls]
                prod_values = [d.value for d in producer_rolls]
                self._on_resolve(
                    f"- {protagonist.name}: P{p_values} vs Prod{prod_values} => {result.outcome}"
                )
            else:
                protagonist_cards = self._state.deck.draw(total_dice)
                producer_cards = self._state.deck.draw(producer_dice_count)
                result = resolve_cards(protagonist.id, protagonist_cards, producer_cards)

                red_fm_cards = sum(
                    1
                    for card in protagonist_cards[-fm_spend:]
                    if is_red(card)
                )
                self._state.producer_budget += red_fm_cards

                p_cards = [f"{c['rank']}-{c['suit'][0].upper()}" for c in protagonist_cards]
                prod_cards = [f"{c['rank']}-{c['suit'][0].upper()}" for c in producer_cards]
                self._on_resolve(
                    f"- {protagonist.name}: P{p_cards} vs Prod{prod_cards} => {result.outcome}"
                )

            scene.results[protagonist.id] = result
            protagonist.fan_mail = max(0, protagonist.fan_mail - fm_spend)

        self._state.producer_budget = max(0, self._state.producer_budget - producer_spend)
        self._state.scenes.append(scene)
        self._state.current_scene_id = scene.id

        if "scene" not in self._state.episode_info:
            self._state.episode_info["scene"] = 0
        self._state.episode_info["scene"] += 1

        self._on_state_change()

    def refresh(self):
        self._sync_participants_ui()
        self._sync_trait_panel()
