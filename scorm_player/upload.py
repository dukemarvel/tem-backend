import os, zipfile, posixpath
from pathlib import Path
from uuid import uuid4
from xml.etree import ElementTree as ET

from django.conf import settings
from django.db import transaction
from .models import Sco

# Full namespace map (SCORM 1.2, 2004 2nd–4th ed.)
NS = {
    "ims":   "http://www.imsproject.org/xsd/imscp_rootv1p1p2",
    "adlcp": "http://www.adlnet.org/xsd/adlcp_rootv1p2",
    "adlcp2":"http://www.adlnet.org/xsd/adlcp_rootv1p2p1",
    "imsss": "http://www.imsglobal.org/xsd/imsss",
    "lom":   "http://ltsc.ieee.org/xsd/imsccv1p0/LOM",
}


def _normalize_href(base, href):
    """
    Resolve href against <resource xml:base> and package root.
    """
    if href is None:
        return ""
    return posixpath.normpath(posixpath.join(base or "", href)).lstrip("/")


def _get_default_org(tree):
    org_root = tree.find("ims:organizations", NS)
    if org_root is None:
        return None
    default_id = org_root.get("default")
    if default_id:
        return org_root.find(f"ims:organization[@identifier='{default_id}']", NS)
    # else fall back to first organization
    return org_root.find("ims:organization", NS)


def _safe_extract(zf: zipfile.ZipFile, path: Path):
    for member in zf.namelist():
        member_path = path / member
        if not str(member_path.resolve()).startswith(str(path.resolve())):
            raise Exception(f"Unsafe path in zip: {member}")
    zf.extractall(path)


@transaction.atomic
def handle_scorm_upload(package):
    """
    1. Extract zip into MEDIA_ROOT/scorm/{package_id}/
    2. Parse imsmanifest.xml robustly.
    3. Create Sco rows for all launchable <item>.
    """
    zip_path = Path(package.file.path)
    extract_dir = Path(settings.MEDIA_ROOT, "scorm", str(package.id))
    extract_dir.mkdir(parents=True, exist_ok=True)

    # -------- unzip
    with zipfile.ZipFile(zip_path) as zf:
        _safe_extract(zf, extract_dir)

    manifest = extract_dir / "imsmanifest.xml"
    if not manifest.exists():
        raise FileNotFoundError("imsmanifest.xml missing in SCORM package")

    # -------- parse XML
    tree = ET.parse(manifest)

    # Build resource map (identifier -> (href, xml:base))
    res_map = {}
    for res in tree.findall(".//ims:resource", NS):
        ident = res.get("identifier")
        href = res.get("href")        # launch file
        base = res.get("{http://www.w3.org/XML/1998/namespace}base", "")
        res_map[ident] = (_normalize_href(base, href), base)

    # Start with default organization (or first)
    org = _get_default_org(tree)
    if org is None:
        raise ValueError("No <organization> found in manifest")

    sequence = 0
    for item in org.iterfind(".//ims:item", NS):
        identref = item.get("identifierref")
        if not identref:
            continue  # non-launchable parent item
        href, base = res_map.get(identref, ("", ""))
        if not href:
            continue
        title = item.findtext("ims:title", default=f"SCO {sequence+1}", namespaces=NS)

        # xml:base on <item> further prefixes launch path
        item_base = item.get("{http://www.w3.org/XML/1998/namespace}base", "")
        launch_url = _normalize_href(posixpath.join(base, item_base), href)

        Sco.objects.create(
            package=package,
            identifier=identref,
            launch_url=launch_url,
            title=title,
            sequence=sequence,
        )
        sequence += 1

    if sequence == 0:
        raise ValueError("Manifest parsed but no launchable SCOs found")