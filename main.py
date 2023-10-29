import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import sqlite3
from tkinter import ttk

#класс главного окна
class EmployeeManagementApp():
    def __init__(self, master):
        self.master = master
        self.master.title("Employee Management App")
        self.master['bg'] = '#FAEBD7'
        self.db = db

        self.conn = sqlite3.connect('employees.db')
        self.create_table()

        #подписи колонок
        self.tree = ttk.Treeview(master)
        scroll = tk.Scrollbar(self.master,command=self.tree.yview, orient='vertical')
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree["columns"] = ("ID", "Name", "Phone", "Email", "Salary")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Имя")
        self.tree.heading("Phone", text="Телефон")
        self.tree.heading("Email", text="E-mail")
        self.tree.heading("Salary", text="Зарплата")
        self.tree.pack(padx=20, pady=20)

        self.create_widgets()
        self.update_treeview()
       
    #метод добавления в БД
    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                phone TEXT,
                email TEXT,
                salary INTEGER
            )
        ''')
        self.conn.commit()

    def create_widgets(self):
        #создание меню
        toolbar = tk.Frame(bg='#FFFAF0', bd=2)
        self.add_img = tk.PhotoImage(file='./img/add.png',height=70, width= 70)
        self.add_button = tk.Button(toolbar,image=self.add_img,bd=5, bg= '#FFF0F5',command=self.add_employee)
        self.add_button.pack( side=tk.LEFT,padx=25, pady= 5)
        self.update_img = tk.PhotoImage(file='./img/update.png',height=70, width= 70)
        self.update_button = tk.Button(toolbar, image=self.update_img, bg= '#FFF0F5', command=self.update_employee)
        self.update_button.pack(side=tk.LEFT, padx=25, pady= 5)
        self.delete_img = tk.PhotoImage(file='./img/delete.png',height=70, width= 70)
        self.delete_button = tk.Button(toolbar,image=self.delete_img, bg= '#FFF0F5', command=self.delete_employee)
        self.delete_button.pack(side=tk.LEFT,padx=25, pady= 5)
        self.search_img = tk.PhotoImage(file='./img/search.png',height=70, width= 70)
        self.search_button = tk.Button(toolbar,image=self.search_img,  bg= '#FFF0F5',command=self.search_employee)
        self.search_button.pack(side=tk.LEFT,padx=25, pady= 5)
        self.undo_img = tk.PhotoImage(file='./img/undo.png', height=64, width=64)
        self.undo_button = tk.Button(toolbar, bg= '#FFF0F5',image=self.undo_img, command=self.undo_action)
        self.undo_button.pack(side=tk.LEFT, padx=25, pady= 5)
        self.refresh_img = tk.PhotoImage(file='./img/refresh.png')
        self.refresh_button = tk.Button(toolbar, bg='#FFF0F5', bd=0, image=self.refresh_img, command=self.view_records)
        self.refresh_button.pack(side=tk.LEFT, padx=25, pady= 5)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # Привязываем функцию двойного щелчка к treeview
        self.tree.bind("<Double-1>", self.on_double_click)

        self.last_action = None  # Чтобы созранить последние действия для отмены

        # вывод данных в виджет таблицы
    def view_records(self):
        # выбираем информацию из БД
        self.db.c.execute('''SELECT * FROM employees''')
        # удаляем все из виджета таблицы
        [self.tree.delete(i) for i in self.tree.get_children()]
        # добавляем в виджет таблицы всю информацию из БД
        [self.tree.insert('', 'end', values=row)
         for row in self.db.c.fetchall()]
        
        #добавдение сотрудника
    def add_employee(self):
        name = simpledialog.askstring("Ввод", "Введите имя сотрудника :")
        phone = simpledialog.askstring("Ввод", "Введите телефон сотрудника:")
        email = simpledialog.askstring("Ввод", "Введите e-mail сотрудника:")
        salary = simpledialog.askinteger("Ввод", "Ввелите зарплату сотрудника:")
        

        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO employees (name, phone, email, salary) VALUES (?, ?, ?, ?)", (name, phone, email, salary))
        self.conn.commit()
        self.update_treeview()
        self.last_action = "add"

        #функция для изменения
    def update_employee(self):
        emp_id = simpledialog.askinteger("Ввод", "Введите ID сотрудника:")

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM employees WHERE id=?", (emp_id,))
        employee = cursor.fetchone()

        if employee:
            name = simpledialog.askstring("Ввод", "Введите измененное имя сотрудника:", initialvalue=employee[1])
            phone = simpledialog.askstring("Ввод", "Введите измененный телефон сотрудника:", initialvalue=employee[2])
            email = simpledialog.askstring("Ввод", "Введите измененный e-mail сотрудника:", initialvalue=employee[3])
            salary = simpledialog.askinteger("Ввод", "Введите измененную зарплату сотрудника:", initialvalue=employee[4])

            cursor.execute("UPDATE employees SET name=?, phone=?, email=?, salary=? WHERE id=?", (name, phone, email, salary, emp_id))
            self.conn.commit()
            self.update_treeview()
            self.last_action = "update"
        else:
            messagebox.showerror("Error", "Сотрудник не найден.")

        # удаление 
    def delete_employee(self):
        emp_id = simpledialog.askinteger("Ввод", "Введите ID сотрудника:")

        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM employees WHERE id=?", (emp_id,))
        self.conn.commit()
        self.update_treeview()
        self.last_action = "delete"

    #поиск
    def search_employee(self):
        name = simpledialog.askstring("Ввод", "Введите имя сотрудника:")

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM employees WHERE name=?", (name,))
        employees = cursor.fetchall()

        if employees:
            self.tree.delete(*self.tree.get_children())
            for employee in employees:
                self.tree.insert("", "end", values=employee)
        else:
            messagebox.showinfo("Info", "Сотрудник с таким именем не найден.")

    def update_treeview(self):
        # Clear the Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM employees")
        employees = cursor.fetchall()

        for employee in employees:
            self.tree.insert("", "end", values=employee)

    def on_double_click(self, event):
        item = self.tree.selection()[0]
        employee_id = self.tree.item(item, "values")[0]  # Получаем ID сотрудника
        messagebox.showinfo("Employee ID", f"Employee ID: {employee_id}")
        
        #действие отмены
    def undo_action(self):
        if self.last_action == "add":
            messagebox.showinfo("Отмена", "Отменить действие добавления сотрудника")
            # Отмена действия добавления
        elif self.last_action == "update":
            messagebox.showinfo("Отмена", "Отмена действия обновления сотрудника")
            # Код действия обновления
        elif self.last_action == "delete":
            messagebox.showinfo("Отмена", "Отмена действия удаления сотрудника")
            # Код действия удаления
        else:
            messagebox.showinfo("Отмена", "Нет предыдущих действия для отмены")

    def on_closing(self):
        self.conn.close()
        self.master.destroy()


# класс БД
class DB:
    def __init__(self):
        self.conn = sqlite3.connect('employees.db')
        self.c = self.conn.cursor()
        
        self.c.execute(
            '''CREATE TABLE IF NOT EXISTS db (id integer primary key AUTOINCREMENT, name text, tel text, email text, salary integer  );''')
        # сохранение изменений БД
        self.conn.commit()

    # метод добавления в БД
    def insert_data(self, name, tel, email, salary):
        self.c.execute('''INSERT INTO db (name, tel, email, salary) VALUES (?, ?, ?, ?)''',
                       (name, tel, email, salary))
        self.conn.commit()


if __name__ == "__main__":
    root = tk.Tk()
    db = DB()
    root.geometry('1250x350')
    app = EmployeeManagementApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()