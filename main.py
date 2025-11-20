from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import TwoLineAvatarIconListItem, ImageLeftWidget
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDFillRoundFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView # Necesario para el scroll del carrito
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty
from requests_handler import RequestsHandler

KV_FILE = 'pos_screen.kv'

# --- CLASE PARA CADA ÍTEM DEL CARRITO ---
class CartItem(MDBoxLayout):
    product_name = StringProperty()
    product_total = StringProperty()
    quantity = NumericProperty()
    product_id = NumericProperty()
    
    def __init__(self, p_id, name, price, qty, callback_update, **kwargs):
        super().__init__(**kwargs)
        self.product_id = p_id
        self.base_price = price
        self.quantity = qty
        self.product_name = name
        self.callback = callback_update # Función para avisar a la pantalla principal
        self.update_display()

    def update_display(self):
        total = self.base_price * self.quantity
        self.product_total = f"S/. {total:.2f}"

    def increase_qty(self):
        self.quantity += 1
        self.update_display()
        self.callback('update', self.product_id, self.quantity)

    def decrease_qty(self):
        if self.quantity > 1:
            self.quantity -= 1
            self.update_display()
            self.callback('update', self.product_id, self.quantity)

    def remove_item(self):
        self.callback('remove', self.product_id, 0)


class ProductListItem(TwoLineAvatarIconListItem):
    '''Clase para los ítems del menú principal'''
    pass

class PosScreen(MDScreen):
    total_text = StringProperty("S/. 0.00")
    cart_info = StringProperty("0 ítems")
    
    available_products = []
    cart_items = {} 
    cart_dialog = None

    def on_enter(self):
        Clock.schedule_once(self.load_products, 0)

    def load_products(self, dt):
        self.available_products = RequestsHandler.get_productos()
        self.update_list(self.available_products)

    def update_list(self, products):
        lista_visual = self.ids.container_productos
        lista_visual.clear_widgets()
        for p in products:
            item = ProductListItem(
                text=p['nombre'],
                secondary_text=f"S/. {p['precio']:.2f}",
                on_release=self.add_to_cart_simple
            )
            item.product_id = p['id']
            item.product_price = p['precio']
            item.product_name = p['nombre']
            
            icon = ImageLeftWidget(source="data/logo/kivy-icon-256.png")
            item.add_widget(icon)
            lista_visual.add_widget(item)

    def filter_list(self, text):
        filtered = [p for p in self.available_products if text.lower() in p['nombre'].lower()]
        self.update_list(filtered)

    # --- LÓGICA DEL CARRITO ---

    def add_to_cart_simple(self, instance_item):
        """Añade 1 unidad (comportamiento rápido desde la lista)."""
        p_id = instance_item.product_id
        if p_id in self.cart_items:
            self.cart_items[p_id]['cantidad'] += 1
        else:
            self.cart_items[p_id] = {
                'nombre': instance_item.product_name, 
                'precio': instance_item.product_price, 
                'cantidad': 1
            }
        self.update_cart_summary()

    def manage_cart_actions(self, action, p_id, new_qty):
        """Callback que recibe las acciones desde los items del carrito (+, -, delete)."""
        if action == 'update':
            self.cart_items[p_id]['cantidad'] = new_qty
        elif action == 'remove':
            del self.cart_items[p_id]
            # Si el diálogo está abierto y borramos algo, hay que refrescar la lista visual del diálogo
            if self.cart_dialog:
                self.populate_cart_dialog_content()
        
        self.update_cart_summary()
        
        # Actualizar el título del diálogo si está abierto
        if self.cart_dialog:
            self.cart_dialog.title = f"Tu Pedido ({self.total_text})"

    def open_cart_dialog(self):
        """Abre la ventana emergente con la lista editable."""
        if not self.cart_items:
            self.show_alert("Carrito Vacío", "No has agregado productos aún.")
            return

        # Creamos el contenedor de la lista
        self.cart_content_layout = MDBoxLayout(orientation='vertical', adaptive_height=True, spacing="10dp")
        
        scroll = MDScrollView(size_hint_y=None, height="300dp")
        scroll.add_widget(self.cart_content_layout)
        
        self.populate_cart_dialog_content()

        self.cart_dialog = MDDialog(
            title=f"Tu Pedido ({self.total_text})",
            type="custom",
            content_cls=scroll,
            buttons=[
                MDFlatButton(text="CERRAR", on_release=lambda x: self.cart_dialog.dismiss()),
                MDFillRoundFlatButton(text="ENVIAR PEDIDO", on_release=self.send_order_from_dialog)
            ]
        )
        self.cart_dialog.open()

    def populate_cart_dialog_content(self):
        """Rellena la lista visual dentro del diálogo."""
        self.cart_content_layout.clear_widgets()
        if not self.cart_items:
            self.cart_dialog.dismiss() # Cerrar si se vacía
            return

        for pid, data in self.cart_items.items():
            item_widget = CartItem(
                p_id=pid,
                name=data['nombre'],
                price=data['precio'],
                qty=data['cantidad'],
                callback_update=self.manage_cart_actions
            )
            self.cart_content_layout.add_widget(item_widget)

    def update_cart_summary(self):
        total = sum(item['precio'] * item['cantidad'] for item in self.cart_items.values())
        count = sum(item['cantidad'] for item in self.cart_items.values())
        self.total_text = f"S/. {total:.2f}"
        self.cart_info = f"{count} ítems"

    def clear_cart(self):
        self.cart_items = {}
        self.update_cart_summary()
        if self.cart_dialog: self.cart_dialog.dismiss()

    def send_order_from_dialog(self, instance):
        if self.cart_dialog: self.cart_dialog.dismiss()
        self.send_order()

    def send_order(self):
        if not self.cart_items:
            self.show_alert("Error", "La canasta está vacía.")
            return

        items_to_send = [{"id": pid, "cantidad": data['cantidad']} for pid, data in self.cart_items.items()]
        
        response = RequestsHandler.post_venta(items_to_send)
        
        if response.get('success'):
            self.show_alert("Éxito", "Pedido enviado correctamente.")
            self.clear_cart()
        else:
            self.show_alert("Error", f"Fallo: {response.get('message')}")

    def show_alert(self, title, text):
        d = MDDialog(title=title, text=text, buttons=[MDFlatButton(text="OK", on_release=lambda x: d.dismiss())])
        d.open()

class CaviApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        Builder.load_file(KV_FILE)
        return PosScreen()

if __name__ == '__main__':
    CaviApp().run()
