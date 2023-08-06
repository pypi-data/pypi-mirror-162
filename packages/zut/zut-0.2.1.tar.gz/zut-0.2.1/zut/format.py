from __future__ import annotations
import re, json, unicodedata, subprocess
from datetime import datetime, date


# -----------------------------------------------------------------------------
# Colors
# -----------------------------------------------------------------------------

FOREGROUND_RED="\033[0;31m%s\033[0;0m"
FOREGROUND_GREEN="\033[0;32m%s\033[0;0m"
FOREGROUND_GRAY="\033[0;90m%s\033[0;0m"
BACKGROUND_RED="\033[0;41m%s\033[0;0m"


# -----------------------------------------------------------------------------
# Decimal numbers
# -----------------------------------------------------------------------------

class _PowerValue():
    def __init__(self, value, unit='B', base="decimal", maxrank=None):
        self.base = base
        if base == "binary":
            power = 1024
            self.rank_labels = []
            for rank in ['', 'Ki', 'Mi', 'Gi', 'Ti']:
                self.rank_labels.append(rank)
                if maxrank and rank != '' and maxrank.upper() == rank[0].upper():
                    break
        elif base == "decimal":
            power = 1000
            self.rank_labels = []
            for rank in ['', 'k', 'M', 'G', 'T']:
                self.rank_labels.append(rank)
                if maxrank and rank != '' and maxrank.upper() == rank[0].upper():
                    break
        else:
            raise ValueError(f'invalid base: {base}')

        self.unit = unit
        self.value = value
        self.rank = 0

        if self.value is None:
            return

        while self.value > power and self.rank < len(self.rank_labels) - 1:
            self.value /= power
            self.rank += 1
        
    def __str__(self):
        if self.value is None:
            return ''
        return ('{:,.1f}' if self.rank > 0 else '{:,.0f}').format(self.value) + ' ' + self.rank_labels[self.rank] + self.unit

def human_bytes(value, base="binary", maxrank=None):
    if value is None:
        return ''

    if base not in ["binary", "decimal", "both"]:
        raise ValueError("invalid base '%s'" % base)
        
    if base in ["binary", "both"]:
        binary_str = str(_PowerValue(value, base="binary", maxrank=maxrank))
        if base == "binary":
            return binary_str

    if base in ["decimal", "both"]:
        decimal_str = str(_PowerValue(value, base="decimal", maxrank=maxrank))
        if base == "decimal":
            return decimal_str
    
    if base == "both":
        return '%-12s' % binary_str + ' (' + decimal_str + ')'


# -----------------------------------------------------------------------------
# Strings
# -----------------------------------------------------------------------------

def slugify(value: str, allow_unicode=False, separator='-', discard_underscores=False, specials=False):
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    
    NOTE: this is a compatible extension of "slugify" function in django.utils.text 
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )

    value = value.lower()

    if specials:
        # french special: replace "l'" and "d'" to ensure hyphen will be kept
        value = value.replace("l'", "l-").replace("d'", "d-")
    
    value = re.sub(r"[^\w\s" + separator + r"]", "", value)
    return re.sub(r"[" + separator + (r"_" if discard_underscores else "") + r"\s]+", separator, value).strip(separator + "_")


def extended_slugify(value: str, allow_unicode=False, separator='-', preserve='', discard_underscores=True, custom_slugs=None):
    if value is None:
        return None
    
    if custom_slugs and value in custom_slugs:
        return custom_slugs[value]

    if preserve:
        values = value.split(preserve)
    else:
        values = [value]

    slugs = []
    for value in values:
        slug = slugify(value, allow_unicode=allow_unicode, separator=separator, discard_underscores=discard_underscores, specials=True)
        slugs.append(slug)
    
    return preserve.join(slugs)


# -----------------------------------------------------------------------------
# JSON
# -----------------------------------------------------------------------------

def extended_json_decode_hook(obj):
    if isinstance(obj, dict):
        for key, value in obj.items():
            obj[key] = extended_json_decode_hook(value)

    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            obj[i] = extended_json_decode_hook(value)

    elif isinstance(obj, str):
        if len(obj) < 10:
            return obj # ignore
        
        if re.match(r'^\d{4}-\d{2}-\d{2}$', obj):
            # date only
            return datetime.strptime(obj, "%Y-%m-%d").date()
        
        m = re.match(r'^(\d{4}-\d{2}-\d{2}T)(\d{2}:\d{2}:\d{2})(\.\d{3,6})?(Z|[\+\-]\d{2}:\d{2})?$', obj)
        if not m:
            return obj # ignore

        datepart = m.group(1) # mandatory
        timepart = m.group(2) # mandatory
        microsecondpart = m.group(3) # optional
        timezone = m.group(4) # optional
        
        # adapt timezone: replace 'Z' with +0000, or +XX:YY with +XXYY
        if timezone == 'Z':
            timezone = '+0000'
        elif timezone:
            timezone = timezone[:-3] + timezone[-2:]
        
        # NOTE: we don't decode XX:XX:XX into a time: too much risky that it's not actually a time
        # if not datepart:
        #     # time only: we only handle non-timezone-aware times, see: DjangoJSONEncoder
        #     if timezone:
        #         return obj

        #     if microsecondpart:
        #         return time.strptime(f"{timepart}{microsecondpart}", "%H:%M:%S.%f")
        #     else:
        #         return time.strptime(f"{timepart}", "%H:%M:%S")

        # datetime
        if microsecondpart:
            return datetime.strptime(f"{datepart}{timepart}{microsecondpart}{timezone}", "%Y-%m-%dT%H:%M:%S.%f%z")
        else:
            return datetime.strptime(f"{datepart}{timepart}{timezone}", "%Y-%m-%dT%H:%M:%S%z")

    return obj


class ExtendedJSONDecoder(json.JSONDecoder):
    """
    JSONDecoder subclass that knows how to decode date/time, decimal types, and UUIDs.
    Reverse of: ExtendedJSONEncoder.
    Usage example: json.loads(data, cls=ExtendedJSONDecoder)
    """
    def __init__(self, **kwargs):
        if not 'object_hook' in kwargs:
            kwargs['object_hook'] = extended_json_decode_hook
        super().__init__(**kwargs)


class ExtendedJSONEncoder(json.JSONEncoder):
    """
    Adapted from: django.core.serializers.json.DjangoJSONEncoder
    Usage example: json.dumps(data, indent=2, cls=ExtendedJSONEncoder)
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def default(self, o):
        # See "Date Time String Format" in the ECMA-262 specification.
        if isinstance(o, datetime):
            r = o.isoformat()
            if o.microsecond and o.microsecond % 1000 == 0:
                r = r[:23] + r[26:]
            if r.endswith("+00:00"):
                r = r[:-6] + "Z"
            return r
        elif isinstance(o, date):
            return o.isoformat()
        # elif isinstance(o, datetime.time):
        #     if is_aware(o):
        #         raise ValueError("JSON can't represent timezone-aware times.")
        #     r = o.isoformat()
        #     if o.microsecond:
        #         r = r[:12]
        #     return r
        # elif isinstance(o, datetime.timedelta):
        #     return duration_iso_string(o)
        # elif isinstance(o, (decimal.Decimal, uuid.UUID, Promise)):
        #     return str(o)
        else:
            return super().default(o)


# -----------------------------------------------------------------------------
# Subprocess
# -----------------------------------------------------------------------------
class SubprocessError(subprocess.CalledProcessError):
    """
    Similar to CalledProcessError but do not show entire cmd (might contain sensitive information)
    and show stdout and stderr.
    """
    def __init__(self, cp: subprocess.CompletedProcess, label=None):
        self.label = label
        super().__init__(cp.returncode, cp.args, cp.stdout, cp.stderr)
    
    def __str__(self):
        msg = f"{self.label if self.label else self.cmd[0]}"
        if self.returncode != 0:
            msg += f" - returncode: {FOREGROUND_GRAY}" % (self.returncode)
        if self.stderr:
            msg += f" - stderr: {FOREGROUND_GRAY}" % (self.stderr.strip() if isinstance(self.stderr, str) else self.stderr)
        if self.stdout:
            msg += f" - stdout: {FOREGROUND_GRAY}" % (self.stdout.strip() if isinstance(self.stdout, str) else self.stdout)
        return msg
