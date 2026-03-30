from tkinter import *
from tkinter import ttk, messagebox
import time

from utils.database_connection import _connect_db

class productGraphClass:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1100x760+320+220")
        self.root.config(bg="white")
        self.root.resizable(False, False)
        self.root.focus_force()

        # ------------ all variables --------------

        self.var_filter_category = StringVar()
        self.var_filter_supplier = StringVar()
        self.var_filter_status = StringVar()

        # ------------ Graph content --------------
        self.setup_inventory_analysis()
 

    # -----------------------------------------------------------------------------------------------------

    def update_content(self):
        con, cur = _connect_db()
        try:
            cur.execute("select * from product")
            product = cur.fetchall()
            self.lbl_product.config(text=f"Total Product\n[ {len(product)} ]")

            cur.execute("select * from category")
            category = cur.fetchall()
            self.lbl_category.config(text=f"Total Category\n[ {len(category)} ]")

            cur.execute("select * from supplier")
            supplier = cur.fetchall()
            self.lbl_supplier.config(text=f"Total Supplier\n[ {len(supplier)} ]")

            # Update chart with current filters and data
            self.apply_filters()

            time_ = time.strftime("%I:%M:%S")
            date_ = time.strftime("%d-%m-%Y")

            self.lbl_clock.config(
                text=f"Report update \t\t Date: {date_}\t\t Time: {time_}"
            )

            self.lbl_clock.after(1000, self.update_content)

        except Exception as ex:
            messagebox.showerror("Error", f"Error due to : {str(ex)}", parent=self.root)
        finally:
            con.close()

    def setup_inventory_analysis(self):
        analysis_frame = LabelFrame(self.root, text="Inventory Analysis", font=("goudy old style", 12, "bold"), bd=2,
                                    relief=RIDGE, bg="white")
        analysis_frame.place(x=50, y=50, width=1000, height=620)

        self.lbl_product = Label(analysis_frame, text="Total Product\n[ 0 ]", bd=2, relief=RIDGE, bg="#607d8b",
                                 fg="white", font=("goudy old style", 12, "bold"))
        self.lbl_product.place(x=10, y=10, width=200, height=60)
        self.lbl_category = Label(analysis_frame, text="Total Category\n[ 0 ]", bd=2, relief=RIDGE, bg="#009688",
                                  fg="white", font=("goudy old style", 12, "bold"))
        self.lbl_category.place(x=220, y=10, width=200, height=60)
        self.lbl_supplier = Label(analysis_frame, text="Total Supplier\n[ 0 ]", bd=2, relief=RIDGE, bg="#ff5722",
                                  fg="white", font=("goudy old style", 12, "bold"))
        self.lbl_supplier.place(x=430, y=10, width=200, height=60)

        # filters
        Label(analysis_frame, text="Category:", font=("goudy old style", 11), bg="white").place(x=10, y=80)
        self.cmb_filter_category = ttk.Combobox(analysis_frame, textvariable=self.var_filter_category, values=["All"],
                                                state='readonly', font=("goudy old style", 11))
        self.cmb_filter_category.place(x=80, y=80, width=160)
        self.cmb_filter_category.current(0)

        Label(analysis_frame, text="Supplier:", font=("goudy old style", 11), bg="white").place(x=260, y=80)
        self.cmb_filter_supplier = ttk.Combobox(analysis_frame, textvariable=self.var_filter_supplier, values=["All"],
                                                state='readonly', font=("goudy old style", 11))
        self.cmb_filter_supplier.place(x=330, y=80, width=160)
        self.cmb_filter_supplier.current(0)

        Label(analysis_frame, text="Status:", font=("goudy old style", 11), bg="white").place(x=510, y=80)
        self.cmb_filter_status = ttk.Combobox(analysis_frame, textvariable=self.var_filter_status,
                                              values=["All", "Active", "Inactive"], state='readonly',
                                              font=("goudy old style", 11))
        self.cmb_filter_status.place(x=565, y=80, width=150)
        self.cmb_filter_status.current(0)

        Button(analysis_frame, text="Apply filters", command=self.apply_filters, font=("goudy old style", 11),
               bg="#4caf50", fg="white", cursor="hand2").place(x=730, y=78, width=120, height=28)
        Button(analysis_frame, text="Remove filters", command=self.clear_filters, font=("goudy old style", 11), bg="#607d8b",
               fg="white", cursor="hand2").place(x=860, y=78, width=120, height=28)

        self.chart_canvas = Canvas(analysis_frame, bg="white", bd=2, relief=RIDGE)
        self.chart_canvas.place(x=10, y=120, width=760, height=460)

        self.lbl_chart_info = Label(analysis_frame, text="", font=("goudy old style", 10), bg="white", fg="black",
                                    justify=LEFT)
        self.lbl_chart_info.place(x=780, y=120, width=210, height=460)

        self.fetch_filter_options()
        self.apply_filters()

    def fetch_filter_options(self):
        con, cur = _connect_db()
        try:
            cur.execute("select distinct Category from product")
            categories = cur.fetchall()
            cat_values = ["All"] + [x[0] for x in categories if x[0] is not None]
            self.cmb_filter_category['values'] = cat_values
            self.cmb_filter_category.current(0)

            cur.execute("select distinct Supplier from product")
            suppliers = cur.fetchall()
            sup_values = ["All"] + [x[0] for x in suppliers if x[0] is not None]
            self.cmb_filter_supplier['values'] = sup_values
            self.cmb_filter_supplier.current(0)
        except Exception as ex:
            messagebox.showerror("Error", f"Error due to : {str(ex)}", parent=self.root)
        finally:
            con.close()

    def get_inventory_summary(self):
        con, cur = _connect_db()
        try:
            where_clause = []
            params = []

            if self.var_filter_category.get() and self.var_filter_category.get() != "All":
                where_clause.append("Category = ?")
                params.append(self.var_filter_category.get())
            if self.var_filter_supplier.get() and self.var_filter_supplier.get() != "All":
                where_clause.append("Supplier = ?")
                params.append(self.var_filter_supplier.get())
            if self.var_filter_status.get() and self.var_filter_status.get() != "All":
                where_clause.append("status = ?")
                params.append(self.var_filter_status.get())

            query = "select name, status, sum(CAST(qty AS INTEGER)) from product"
            if where_clause:
                query += " where " + " and ".join(where_clause)
            query += " group by name, status"

            cur.execute(query, params)
            rows = cur.fetchall()

            product_summary = {}
            for name, status, qty_sum in rows:
                if name is None:
                    continue
                name = str(name)
                st = str(status).title()
                qty_value = int(qty_sum) if qty_sum is not None else 0
                if name not in product_summary:
                    product_summary[name] = {"Active": 0, "Inactive": 0}
                if st in product_summary[name]:
                    product_summary[name][st] = qty_value

            total = sum(v["Active"] + v["Inactive"] for v in product_summary.values())
            return {"products": product_summary, "total": total}
        except Exception as ex:
            messagebox.showerror("Error", f"Error due to : {str(ex)}", parent=self.root)
            return {"products": {}, "total": 0}
        finally:
            con.close()

    def draw_inventory_barchart(self, summary):
        self.chart_canvas.delete("all")

        products = summary.get("products", {})
        total = summary.get("total", 0)

        if total == 0 or len(products) == 0:
            self.chart_canvas.create_text(380, 150, text="Empty inventory", fill="gray",
                                          font=("goudy old style", 14, "bold"))
            self.lbl_chart_info.config(text="No data to render chart")
            return

        max_value = max((v["Active"] + v["Inactive"] for v in products.values()), default=1)
        top_margin = 30
        bottom_margin = 30
        height = 460 - top_margin - bottom_margin
        scale = height / max_value

        # canvas axis
        y_base = 460 - bottom_margin
        self.chart_canvas.create_line(50, y_base, 760, y_base, width=2)
        self.chart_canvas.create_line(50, top_margin, 50, y_base, width=2)

        # stacked bars for each product
        product_names = sorted(products.keys())
        max_bars = 8
        product_names = product_names[:max_bars]

        bar_width = 70
        space = 40
        x = 80

        for name in product_names:
            counts = products[name]
            active = counts.get("Active", 0)
            inactive = counts.get("Inactive", 0)

            y_active_top = y_base - active * scale
            y_inactive_top = y_active_top - inactive * scale

            if inactive > 0:
                self.chart_canvas.create_rectangle(x, y_inactive_top, x + bar_width, y_active_top, fill="#ffccbc", outline="black")
            if active > 0:
                self.chart_canvas.create_rectangle(x, y_active_top, x + bar_width, y_base, fill="#4caf50", outline="black")

            self.chart_canvas.create_text(x + bar_width / 2, y_base + 15, text=name, font=("goudy old style", 9), angle=45)
            self.chart_canvas.create_text(x + bar_width / 2, y_inactive_top - 10, text=str(active + inactive), font=("goudy old style", 9, "bold"))

            x += bar_width + space

        self.lbl_chart_info.config(text=(f"Filtro: Cat={self.var_filter_category.get() or 'All'}\n"
                                         f"Proveedor={self.var_filter_supplier.get() or 'All'}\n"
                                         f"Status={self.var_filter_status.get() or 'All'}\n"
                                         f"Total={total}\n"
                                         f"Productos mostrados={len(product_names)}"))

    def apply_filters(self):
        summary = self.get_inventory_summary()
        self.draw_inventory_barchart(summary)

    def clear_filters(self):
        self.var_filter_category.set("All")
        self.var_filter_supplier.set("All")
        self.var_filter_status.set("All")
        self.fetch_filter_options()
        self.apply_filters()


if __name__ == "__main__":
    root = Tk()
    obj = productGraphClass(root)
    root.mainloop()