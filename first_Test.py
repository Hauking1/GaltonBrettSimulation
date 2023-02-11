import time
import math
from wgpu.gui.auto import WgpuCanvas, run
import pygfx as gfx

renderer = gfx.renderers.WgpuRenderer(WgpuCanvas())
scene = gfx.Scene()

sphere = gfx.Mesh(
    gfx.sphere_geometry(10, 40, 30),
    gfx.MeshPhongMaterial(),
)
sphere.position.x = 10
sphere.rotation.set_from_euler(gfx.linalg.Euler(math.pi / 6, math.pi / 6))
scene.add(sphere)

light = gfx.DirectionalLight("#0040ff", 3)
light.position.x = 15
light.position.y = 20

scene.add(light.add(gfx.DirectionalLightHelper(10)))


scene.add(gfx.AmbientLight("#fff", 0.2))

camera = gfx.PerspectiveCamera(60, 16 / 9)
camera.position.z = 60

controller = gfx.OrbitController(camera.position.clone())
controller.add_default_event_handlers(renderer, camera)


def animate():
    controller.update_camera(camera)
    t = time.time() * 0.1
    renderer.render(scene, camera)
    renderer.request_draw()


if __name__ == "__main__":
    renderer.request_draw(animate)
    run()