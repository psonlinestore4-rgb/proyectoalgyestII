import json
import os
import datetime
import shlex
import base64

# Miguel Tovar, José Millan, José Mijares

# =====================================================================
# MÓDULO 5: Registro de Errores (Lista Enlazada Simple)[cite: 1, 3]
# =====================================================================
class LogNode:
    def __init__(self, code, description):
        self.date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.code = code
        self.description = description
        self.next = None

class SystemLog:
    def __init__(self):
        self.head = None

    def add_log(self, code, description):
        new_node = LogNode(code, description)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node

    def display(self):
        print("\n--- LOG DE SISTEMA ---")
        current = self.head
        if not current:
            print("No hay errores registrados.")
        while current:
            print(f"[{current.date}] ERROR {current.code}: {current.description}")
            current = current.next
        print("----------------------\n")

sys_log = SystemLog()

# =====================================================================
# MÓDULO 3: Gestión de Restauración (Pila / Stack)[cite: 1, 3]
# =====================================================================
class StackNode:
    def __init__(self, state):
        self.state = state
        self.next = None

class StateStack:
    def __init__(self):
        self.top = None

    def push(self, state):
        new_node = StackNode(state)
        new_node.next = self.top
        self.top = new_node

    def pop(self):
        if not self.top:
            return None
        state = self.top.state
        self.top = self.top.next
        return state

    def to_list(self):
        items = []
        current = self.top
        while current:
            items.append(current.state)
            current = current.next
        return items[::-1] 

    def from_list(self, data_list):
        for state in data_list:
            self.push(state)

# =====================================================================
# MÓDULO 2: Contexto de Conversación (Cola / Queue)[cite: 1, 3]
# =====================================================================
class QueueNode:
    def __init__(self, message):
        self.message = message
        self.next = None

class ContextQueue:
    def __init__(self, max_size=10):
        self.front = None
        self.rear = None
        self.size = 0
        self.max_size = max_size

    def enqueue(self, message):
        # Desencolar automáticamente si se excede la ventana de contexto
        if self.size >= self.max_size:
            self.dequeue()
        new_node = QueueNode(message)
        if self.rear is None:
            self.front = self.rear = new_node
        else:
            self.rear.next = new_node
            self.rear = new_node
        self.size += 1

    def dequeue(self):
        if self.front is None:
            return None
        temp = self.front
        self.front = temp.next
        if self.front is None:
            self.rear = None
        self.size -= 1
        return temp.message

    def to_list(self):
        items = []
        current = self.front
        while current:
            items.append(current.message)
            current = current.next
        return items

    def from_list(self, data_list):
        for msg in data_list:
            self.enqueue(msg)

    def display(self):
        current = self.front
        while current:
            print(f"> {current.message}")
            current = current.next

# =====================================================================
# MÓDULO 1: Configuración de Chatbots (Lista Enlazada Doble)[cite: 1, 3]
# =====================================================================
class BotNode:
    def __init__(self, bot_id, name, model, api_key, system_instruction, temperatura=0.7, already_protected=False):
        self.id = str(bot_id)
        self.name = name
        self.model = model
        # API Key protegida con Base64 (requisito Módulo 1)
        if already_protected:
            self.api_key = api_key
        else:
            self.api_key = base64.b64encode(api_key.encode()).decode()
        self.system_instruction = system_instruction
        self.temperatura = temperatura  # Atributo requerido por Módulo 3 y 6
        
        # Punteros a estructuras hijas
        self.queue = ContextQueue(max_size=10)  # Ventana de contexto N=10
        self.stack = StateStack()
        
        # Punteros de lista doble
        self.prev = None
        self.next = None

    def get_api_key(self):
        return base64.b64decode(self.api_key.encode()).decode()

    def save_state(self):
        # Guarda el estado actual antes de una modificación
        state = {
            "name": self.name,
            "model": self.model,
            "system_instruction": self.system_instruction,
            "temperatura": self.temperatura
        }
        self.stack.push(state)

    def restore_state(self):
        state = self.stack.pop()
        if state:
            self.name = state["name"]
            self.model = state["model"]
            self.system_instruction = state["system_instruction"]
            self.temperatura = state.get("temperatura", 0.7)
            return True
        return False

class BotManager:
    def __init__(self):
        self.head = None
        self.tail = None

    def append(self, bot_node):
        if not self.head:
            self.head = self.tail = bot_node
        else:
            self.tail.next = bot_node
            bot_node.prev = self.tail
            self.tail = bot_node

    def find(self, bot_id):
        current = self.head
        while current:
            if current.id == str(bot_id):
                return current
            current = current.next
        return None

    def consultar(self, bot_id):
        # Operación de consulta requerida por Módulo 1
        bot = self.find(bot_id)
        if bot:
            return {
                "id": bot.id,
                "name": bot.name,
                "model": bot.model,
                "system_instruction": bot.system_instruction,
                "temperatura": bot.temperatura,
                "mensajes": bot.queue.to_list()
            }
        return None

    def remove(self, bot_id):
        node = self.find(bot_id)
        if not node:
            return False
            
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next
            
        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev
            
        node.prev = None
        node.next = None
        
        node.queue.front = node.queue.rear = None
        node.stack.top = None
        
        return True

    def display_all(self):
        current = self.head
        print(f"\n{'ID':<5} | {'Nombre':<15} | {'Modelo':<15} | {'Temp':<5}")
        print("-" * 45)
        while current:
            print(f"{current.id:<5} | {current.name:<15} | {current.model:<15} | {current.temperatura:<5}")
            current = current.next
        print("-" * 45)

# =====================================================================
# MÓDULO 4: Persistencia y Serialización[cite: 1, 3]
# =====================================================================
class DataManager:
    def __init__(self):
        self.db_path = self._load_config()

    def _load_config(self):
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
                return config.get('db_path', 'gemini_data.json')
        except FileNotFoundError:
            sys_log.add_log("CFG_ERR", "Archivo config.json no encontrado. Usando default.")
            return 'gemini_data.json'

    def save_data(self, bot_manager):
        data = []
        current = bot_manager.head
        while current:
            bot_data = {
                "id": current.id,
                "name": current.name,
                "model": current.model,
                "api_key": current.api_key,
                "system_instruction": current.system_instruction,
                "temperatura": current.temperatura,
                "queue": current.queue.to_list(),
                "stack": current.stack.to_list()
            }
            data.append(bot_data)
            current = current.next
            
        with open(self.db_path, 'w') as f:
            json.dump(data, f, indent=4)
        print("[+] Datos guardados correctamente en JSON.")

    def load_data(self, bot_manager):
        if not os.path.exists(self.db_path):
            print("[!] Archivo de base de datos no encontrado. Cargando datos por defecto.")
            self._load_default_data(bot_manager)
            return

        try:
            with open(self.db_path, 'r') as f:
                data = json.load(f)
                for b_data in data:
                    bot = BotNode(b_data["id"], b_data["name"], b_data["model"],
                                  b_data["api_key"], b_data["system_instruction"],
                                  b_data.get("temperatura", 0.7),
                                  already_protected=True)
                    bot.queue.from_list(b_data["queue"])
                    bot.stack.from_list(b_data["stack"])
                    bot_manager.append(bot)
            print("[+] Datos y punteros restaurados correctamente.")
        except Exception as e:
            sys_log.add_log("LOAD_ERR", f"Error al cargar JSON: {str(e)}")

    def _load_default_data(self, bot_manager):
        default_bot = BotNode("1", "Asistente Code", "gemini-1.5-flash", "API_KEY_HIDDEN", 
                              "Eres un experto en Python.", temperatura=0.7)
        bot_manager.append(default_bot)

# =====================================================================
# MÓDULO 6: Patrón de Diseño Comandos e Interfaz CLI[cite: 1, 3]
# =====================================================================
class SystemContext:
    def __init__(self):
        self.bot_manager = BotManager()
        self.data_manager = DataManager()
        self.active_bot = None
        self.data_manager.load_data(self.bot_manager)

class Command:
    def execute(self, context, args):
        pass

class ListCommand(Command):
    def execute(self, context, args):
        context.bot_manager.display_all()

class SelectCommand(Command):
    def execute(self, context, args):
        if not args:
            print("Error: Especifique un ID. Uso: /select <id>")
            return
        bot = context.bot_manager.find(args[0])
        if bot:
            context.active_bot = bot
            print(f"[*] Bot '{bot.name}' (ID: {bot.id}) seleccionado.")
        else:
            sys_log.add_log("BOT_404", f"Intento de seleccionar bot inexistente ID: {args[0]}")
            print("[!] Error: ID no encontrado.")

class ChatCommand(Command):
    def execute(self, context, args):
        if not context.active_bot:
            print("[!] Seleccione un bot primero con /select <id>")
            return
        if not args:
            print("Error: Escriba un mensaje. Uso: /chat \"Hola\"")
            return
            
        mensaje = " ".join(args)
        context.active_bot.queue.enqueue(mensaje)
        print(f"[Simulación - Respuesta de {context.active_bot.name} generada y encolada]")

class EditCommand(Command):
    def execute(self, context, args):
        if not context.active_bot:
            print("[!] Seleccione un bot primero.")
            return
        if len(args) < 2:
            print("Uso: /edit <campo> <valor>. Campos: nombre, modelo, prompt, temperatura")
            return
            
        campo = args[0].lower()
        valor = " ".join(args[1:])
        
        context.active_bot.save_state()  # Guarda snapshot antes de modificar
        
        if campo == "nombre":
            context.active_bot.name = valor
        elif campo == "modelo":
            context.active_bot.model = valor
        elif campo == "prompt":
            context.active_bot.system_instruction = valor
        elif campo == "temperatura":
            try:
                context.active_bot.temperatura = float(valor)
            except ValueError:
                print("[!] La temperatura debe ser un número (ej. 0.5)")
                context.active_bot.restore_state()
                return
        else:
            print("[!] Campo no reconocido.")
            context.active_bot.restore_state()
            return
            
        print(f"[+] {campo} actualizado correctamente.")

class DeleteCommand(Command):
    def execute(self, context, args):
        if not args:
            print("Error: Especifique un ID. Uso: /delete <id>")
            return
        
        if context.active_bot and context.active_bot.id == args[0]:
            context.active_bot = None 

        exito = context.bot_manager.remove(args[0])
        if exito:
            print(f"[+] Bot ID {args[0]} eliminado de la red.")
        else:
            sys_log.add_log("DEL_ERR", f"Intento de borrar ID inexistente: {args[0]}")
            print("[!] Error: ID no encontrado.")

class UndoCommand(Command):
    def execute(self, context, args):
        if not context.active_bot:
            print("[!] Seleccione un bot primero.")
            return
            
        if context.active_bot.restore_state():
            print("[+] Estado anterior restaurado desde la pila con exito.")
        else:
            print("[-] No hay estados previos en la pila para restaurar.")

class CurrentCommand(Command):
    def execute(self, context, args):
        bot = context.active_bot
        if not bot:
            print("[!] Seleccione un bot primero.")
            return
        print(f"\n--- CONTEXTO ACTUAL: {bot.name} ---")
        print(f"Modelo: {bot.model}")
        print(f"Instrucción: {bot.system_instruction}")
        print(f"Temperatura: {bot.temperatura}")
        print("Historial de mensajes (Cola dinámica):")
        bot.queue.display()
        print("----------------------------------\n")

class LogCommand(Command):
    def execute(self, context, args):
        sys_log.display()

class CreateCommand(Command):
    def execute(self, context, args):
        if len(args) < 3:
            print("Uso: /create <id> <nombre> <modelo>")
            return
        if context.bot_manager.find(args[0]):
            print("[!] Ese ID ya existe en la lista.")
            return
        nuevo_bot = BotNode(args[0], args[1], args[2], "API_KEY", "Default instruction")
        context.bot_manager.append(nuevo_bot)
        print(f"[+] Bot {args[1]} enlazado correctamente.")

class CLI:
    def __init__(self):
        self.context = SystemContext()
        self.commands = {
            "/list": ListCommand(),
            "/select": SelectCommand(),
            "/chat": ChatCommand(),
            "/edit": EditCommand(),
            "/delete": DeleteCommand(),
            "/undo": UndoCommand(),
            "/current": CurrentCommand(),
            "/log": LogCommand(),
            "/create": CreateCommand()
        }

    def start(self):
        print("="*50)
        print("   GEMINI MESH - SISTEMA DE ORQUESTACIÓN")
        print("="*50)
        print("Comandos: /list, /select, /chat, /edit, /delete, /undo, /current, /log, /create, /save, /exit, /exit.")
        
        while True:
            try:
                prefix = f"({self.context.active_bot.name}) " if self.context.active_bot else ""
                user_input = input(f"\n{prefix}mesh> ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() == "/exit":
                    self.context.data_manager.save_data(self.context.bot_manager)
                    print("Saliendo y guardando datos en JSON...")
                    break
                    
                elif user_input.lower() == "/exit.":
                    self.context.active_bot = None
                    print("Has salido de la sesión del chatbot actual.")
                    continue
                    
                elif user_input.lower() == "/save":
                    self.context.data_manager.save_data(self.context.bot_manager)
                    continue

                parsed_input = shlex.split(user_input)
                cmd_str = parsed_input[0].lower()
                args = parsed_input[1:]

                if cmd_str in self.commands:
                    self.commands[cmd_str].execute(self.context, args)
                else:
                    print(f"[!] Comando '{cmd_str}' no reconocido. Usa comandos de la lista (con '/').")
                    
            except ValueError as ve:
                sys_log.add_log("PARSE_ERR", "Error al procesar comillas o sintaxis de comando.")
                print("[!] Revise la sintaxis de su comando. Posiblemente le falte cerrar una comilla.")
            except Exception as e:
                sys_log.add_log("SYS_ERR", str(e))
                print(f"[!] Ha ocurrido un error inesperado. Consulte el /log para auditar el fallo.")

if __name__ == "__main__":
    cli = CLI()
    cli.start()