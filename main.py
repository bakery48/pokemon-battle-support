import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
import threading

CONFIG_FILE = "config.json"


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"api_key": "", "my_party": ["", "", "", "", "", ""]}


def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


class PokemonBattleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ポケモンバトルサポート")
        self.root.geometry("860x780")
        self.root.resizable(True, True)
        self.root.configure(bg="#1a1a2e")

        self.config = load_config()
        self._setup_styles()
        self._build_ui()

    # ------------------------------------------------------------------ styles
    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        bg = "#1a1a2e"
        card = "#16213e"
        accent = "#e94560"
        fg = "#eaeaea"
        entry_bg = "#0f3460"
        btn_bg = "#e94560"

        style.configure("TFrame", background=bg)
        style.configure("Card.TFrame", background=card, relief="flat")
        style.configure(
            "TLabel",
            background=card,
            foreground=fg,
            font=("Yu Gothic UI", 10),
        )
        style.configure(
            "Title.TLabel",
            background=bg,
            foreground=accent,
            font=("Yu Gothic UI", 14, "bold"),
        )
        style.configure(
            "Section.TLabel",
            background=card,
            foreground=accent,
            font=("Yu Gothic UI", 11, "bold"),
        )
        style.configure(
            "TEntry",
            fieldbackground=entry_bg,
            foreground=fg,
            insertcolor=fg,
            font=("Yu Gothic UI", 10),
        )
        style.configure(
            "Accent.TButton",
            background=btn_bg,
            foreground="white",
            font=("Yu Gothic UI", 11, "bold"),
            borderwidth=0,
            focuscolor="none",
        )
        style.map(
            "Accent.TButton",
            background=[("active", "#c73652"), ("disabled", "#555")],
        )
        style.configure(
            "Sub.TButton",
            background="#0f3460",
            foreground=fg,
            font=("Yu Gothic UI", 9),
            borderwidth=0,
            focuscolor="none",
        )
        style.map("Sub.TButton", background=[("active", "#1a4a80")])

    # ----------------------------------------------------------------- UI build
    def _build_ui(self):
        root_pad = {"padx": 12, "pady": 6}

        # ── Title ──
        ttk.Label(
            self.root, text="ポケモンバトルサポート", style="Title.TLabel"
        ).pack(pady=(14, 4))

        # ── API Key ──
        api_card = ttk.Frame(self.root, style="Card.TFrame", padding=10)
        api_card.pack(fill=tk.X, **root_pad)

        ttk.Label(api_card, text="Gemini APIキー", style="Section.TLabel").grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 6)
        )
        ttk.Label(api_card, text="APIキー :").grid(row=1, column=0, sticky="w")
        self.api_key_var = tk.StringVar(value=self.config.get("api_key", ""))
        api_entry = ttk.Entry(api_card, textvariable=self.api_key_var, show="*", width=52)
        api_entry.grid(row=1, column=1, sticky="ew", padx=(6, 6))
        ttk.Button(
            api_card, text="保存", style="Sub.TButton",
            command=self._save_api_key
        ).grid(row=1, column=2)
        api_card.columnconfigure(1, weight=1)

        # ── My Party ──
        my_card = ttk.Frame(self.root, style="Card.TFrame", padding=10)
        my_card.pack(fill=tk.X, **root_pad)

        ttk.Label(my_card, text="自分のパーティ（6匹）", style="Section.TLabel").grid(
            row=0, column=0, columnspan=7, sticky="w", pady=(0, 6)
        )
        self.my_entries = []
        for i in range(6):
            col = i * 2
            ttk.Label(my_card, text=f"{i+1}.").grid(row=1, column=col, padx=(8 if i else 0, 2))
            var = tk.StringVar(value=self.config.get("my_party", [""] * 6)[i])
            e = ttk.Entry(my_card, textvariable=var, width=12)
            e.grid(row=1, column=col + 1, padx=(0, 6))
            self.my_entries.append(var)

        ttk.Button(
            my_card, text="パーティを保存", style="Sub.TButton",
            command=self._save_my_party
        ).grid(row=2, column=0, columnspan=12, pady=(8, 0))

        # ── Opponent Party ──
        opp_card = ttk.Frame(self.root, style="Card.TFrame", padding=10)
        opp_card.pack(fill=tk.X, **root_pad)

        opp_header = ttk.Frame(opp_card, style="Card.TFrame")
        opp_header.grid(row=0, column=0, columnspan=7, sticky="ew", pady=(0, 6))
        ttk.Label(opp_header, text="相手のパーティ（6匹）", style="Section.TLabel").pack(side=tk.LEFT)
        ttk.Button(
            opp_header, text="クリア", style="Sub.TButton",
            command=self._clear_opponent
        ).pack(side=tk.RIGHT)

        self.opp_entries = []
        for i in range(6):
            col = i * 2
            ttk.Label(opp_card, text=f"{i+1}.").grid(row=1, column=col, padx=(8 if i else 0, 2))
            var = tk.StringVar()
            e = ttk.Entry(opp_card, textvariable=var, width=12)
            e.grid(row=1, column=col + 1, padx=(0, 6))
            self.opp_entries.append(var)

        # ── Analyze Button ──
        btn_frame = ttk.Frame(self.root, style="TFrame")
        btn_frame.pack(pady=10)
        self.analyze_btn = ttk.Button(
            btn_frame,
            text="  分析する  ",
            style="Accent.TButton",
            command=self._start_analysis,
        )
        self.analyze_btn.pack(ipadx=20, ipady=6)

        # ── Result ──
        res_card = ttk.Frame(self.root, style="Card.TFrame", padding=10)
        res_card.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        ttk.Label(res_card, text="分析結果", style="Section.TLabel").pack(anchor="w", pady=(0, 6))

        self.result_text = scrolledtext.ScrolledText(
            res_card,
            wrap=tk.WORD,
            font=("Yu Gothic UI", 10),
            bg="#0f3460",
            fg="#eaeaea",
            insertbackground="white",
            relief="flat",
            padx=8,
            pady=8,
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)

    # ----------------------------------------------------------------- actions
    def _save_api_key(self):
        self.config["api_key"] = self.api_key_var.get().strip()
        save_config(self.config)
        messagebox.showinfo("保存完了", "APIキーを保存しました。")

    def _save_my_party(self):
        self.config["my_party"] = [v.get().strip() for v in self.my_entries]
        save_config(self.config)
        messagebox.showinfo("保存完了", "自分のパーティを保存しました。")

    def _clear_opponent(self):
        for v in self.opp_entries:
            v.set("")

    def _start_analysis(self):
        api_key = self.api_key_var.get().strip()
        if not api_key:
            messagebox.showerror("エラー", "Gemini APIキーを入力してください。")
            return

        my_party = [v.get().strip() for v in self.my_entries if v.get().strip()]
        opp_party = [v.get().strip() for v in self.opp_entries if v.get().strip()]

        if not my_party:
            messagebox.showerror("エラー", "自分のパーティを入力してください。")
            return
        if len(opp_party) < 2:
            messagebox.showerror("エラー", "相手のパーティを2匹以上入力してください。")
            return

        self.analyze_btn.config(state=tk.DISABLED)
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, "分析中...しばらくお待ちください。\n")

        t = threading.Thread(
            target=self._do_analysis, args=(api_key, my_party, opp_party), daemon=True
        )
        t.start()

    def _do_analysis(self, api_key, my_party, opp_party):
        try:
            import time
            import google.generativeai as genai

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.0-flash")

            my_str = "、".join(my_party)
            opp_str = "、".join(opp_party)

            prompt = f"""あなたはポケモン対戦（シングルバトル）の上級アナリストです。
以下の情報をもとに、相手プレイヤーの行動を詳しく予測してください。

━━━━━━━━━━━━━━━━━━━━
【自分のパーティ（6匹）】
{my_str}

【相手のパーティ（6匹）】
{opp_str}
━━━━━━━━━━━━━━━━━━━━

以下の各項目について、具体的な理由を添えて分析してください。

1. 【相手の選出予想（3匹）】
   - 最も可能性が高い選出3匹を順位付きで予想
   - 各ポケモンを選ぶ理由（タイプ相性・役割・メタ的観点）

2. 【先頭ポケモン予想】
   - 相手が最初に繰り出す可能性が高いポケモン（上位2匹）
   - その理由（展開・起点作り・対面性能など）

3. 【相手の戦略予想】
   - 相手パーティ全体のコンセプト・スタイル分析
   - 自分のパーティに対して狙ってくる戦略

4. 【こちらの推奨選出・立ち回り】
   - 対策として推奨する自分の選出3匹
   - 各ポケモンの役割と立ち回りの要点

各ポケモンのタイプ・特性・代表的な持ち物・技構成・メタにおける役割を踏まえて分析してください。
"""

            # リトライ（最大3回、指数バックオフ）
            last_err = None
            for attempt in range(3):
                try:
                    response = model.generate_content(prompt)
                    result = response.text
                    self.root.after(0, self._show_result, result)
                    return
                except Exception as e:
                    last_err = e
                    err_str = str(e)
                    # 429 レート制限なら待機してリトライ
                    if "429" in err_str:
                        wait = 15 * (2 ** attempt)  # 15s, 30s, 60s
                        self.root.after(
                            0,
                            self._set_status,
                            f"APIレート制限中... {wait}秒後に再試行します（{attempt+1}/3）",
                        )
                        time.sleep(wait)
                    else:
                        raise
            raise last_err

        except ImportError:
            self.root.after(
                0,
                self._show_result,
                "エラー: google-generativeai がインストールされていません。\n"
                "run.bat を実行するか、以下のコマンドを実行してください:\n"
                "  pip install google-generativeai",
            )
        except Exception as e:
            self.root.after(0, self._show_result, f"エラーが発生しました:\n{e}")

    def _set_status(self, text):
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, text)

    def _show_result(self, text):
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, text)
        self.analyze_btn.config(state=tk.NORMAL)


# ---------------------------------------------------------------------------
def main():
    root = tk.Tk()
    app = PokemonBattleApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
