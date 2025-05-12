import zipfile
import os
import tempfile
import uuid
import base64
import xml.etree.ElementTree as ET

def parse_bcfzip_to_navisworks_xml(bcfzip_path, output_xml_path):
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(bcfzip_path, 'r') as zip_ref:
            zip_ref.extractall(tmpdir)

        # Создаем корневой элемент XML
        exchange_el = ET.Element("exchange")
        viewpoints_el = ET.SubElement(exchange_el, "viewpoints")

        for folder in sorted(os.listdir(tmpdir)):
            issue_path = os.path.join(tmpdir, folder)
            if not os.path.isdir(issue_path):
                continue

            markup_file = os.path.join(issue_path, "markup.bcf")
            bcfv_files = sorted([f for f in os.listdir(issue_path) if f.endswith(".bcfv")])
            snapshot_file = os.path.join(issue_path, "snapshot.png")

            if not os.path.exists(markup_file) or not bcfv_files:
                continue

            # Читаем Title и Description
            markup_root = ET.parse(markup_file).getroot()
            title = markup_root.findtext("Topic/Title") or "Untitled"
            description = markup_root.findtext("Topic/Description") or ""

            # Читаем первую камерную позицию
            bcfv_root = ET.parse(os.path.join(issue_path, bcfv_files[0])).getroot()
            camera_el = bcfv_root.find(".//PerspectiveCamera")
            if camera_el is None:
                continue

            def extract_vector(parent, tag):
                vec = parent.find(tag)
                return {
                    "x": vec.findtext("X", "0"),
                    "y": vec.findtext("Y", "0"),
                    "z": vec.findtext("Z", "0")
                } if vec is not None else {"x": "0", "y": "0", "z": "0"}

            position = extract_vector(camera_el, "CameraViewPoint")
            direction = extract_vector(camera_el, "CameraDirection")
            up = extract_vector(camera_el, "CameraUpVector")
            fov = camera_el.findtext("FieldOfView", "60")

            # Добавляем viewpoint в XML
            vp = ET.SubElement(viewpoints_el, "viewpoint", {
                "guid": str(uuid.uuid4()),
                "name": title
            })

            cam = ET.SubElement(vp, "camera", {"type": "perspective"})
            ET.SubElement(cam, "position", position)
            # Target = position + direction
            target = {
                axis: str(float(position[axis]) + float(direction[axis]))
                for axis in ['x', 'y', 'z']
            }
            ET.SubElement(cam, "target", target)
            ET.SubElement(cam, "up", up)
            ET.SubElement(cam, "fov").text = fov

            # Комментарий
            comments = ET.SubElement(vp, "comments")
            ET.SubElement(comments, "comment").text = description

            # Скриншот
            if os.path.exists(snapshot_file):
                with open(snapshot_file, "rb") as img:
                    encoded = base64.b64encode(img.read()).decode("utf-8")
                    thumb = ET.SubElement(vp, "thumbnail")
                    thumb.text = encoded

        # Запись XML
        tree = ET.ElementTree(exchange_el)
        ET.indent(tree, space="  ")
        tree.write(output_xml_path, encoding="utf-8", xml_declaration=True)

# Пример запуска
parse_bcfzip_to_navisworks_xml("tst.bcf", "navisworks_viewpoints.xml")
