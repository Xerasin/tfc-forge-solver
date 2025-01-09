import struct
import hashlib
import numpy as np

# Constants from Java code
GOLDEN_RATIO_64 = -7046029254386353131
SILVER_RATIO_64 = 7640891576956012809
SEED_UNIQUIFIER = 8682522807148012


def to_signed(n, width=64):
    """Convert an integer to a signed integer with specified bit width."""
    if n >= (1 << (width - 1)):
        return n - (1 << width)
    return n

def to_unsigned(n, width=64):
    """Convert a signed integer to an unsigned integer with specified bit width."""
    if n < 0:
        return n + (1 << width)
    return n

def mix_stafford13(seed):
    # Ensure seed is treated as a 64-bit unsigned integer for operations
    seed = to_unsigned(seed)
    seed ^= seed >> 30
    seed = (seed * -4658895280553007687) & ((1 << 64) - 1)
    seed ^= seed >> 27
    seed = (seed * -7723592293110705685) & ((1 << 64) - 1)
    seed ^= seed >> 31
    return to_signed(seed)

def upgrade_seed_to_128bit(seed):
    seed = to_signed(seed ^ 0x6A09E667F3BCC909)
    seed2 = (seed + GOLDEN_RATIO_64) & ((1 << 64) - 1)
    return mix_stafford13(seed), mix_stafford13(seed2)

def from_bytes(byte_array):
    if len(byte_array) != 8:
        raise ValueError("Byte array must be 8 bytes long")
    
    value = struct.unpack('<Q', byte_array)[0]
    
    if value >= 2**63:
        value -= 2**64

def from_64bit_binary(binary_str):
    if len(binary_str) != 64:
        raise ValueError("The binary string must be exactly 64 bits long.")
    return int(binary_str, 2)

def to_64bit_binary(value):
    if value < 0:
        value = (1 << 64) + value
    return f'{value:064b}'

def rotate_left(value, rotations, width=64):
    value = value & ((1 << width) - 1)

    rotations = rotations % width
    rotated_value = ((value << rotations) | (value >> (width - rotations))) & ((1 << width) - 1)
    
    return rotated_value

def shift_left_without_wrap(value, shift, width=64):
    value_unsigned = (value + (1 << 64)) & ((1 << 64) - 1)
    shifted_value = value_unsigned << shift
    mask = (1 << width) - 1
    shifted_value &= mask
    return to_signed(shifted_value)

def to_signed(n, width=64):
    if n >= (1 << (width - 1)):
        return n - (1 << width)
    return n

def add_with_wrap_around(a, b, width=64):
    return to_signed((a + b) & ((1 << width) - 1), width)

def update_seeds(seed_lo, seed_hi):

    p1 = rotate_left(seed_lo, 49)
    p2 = seed_hi ^ seed_lo
    a = to_64bit_binary(p2)
    p3 = shift_left_without_wrap(p2, 21)



    new_seed_lo = p1 ^ p2 ^ p3
    new_seed_hi = rotate_left(seed_hi ^ seed_lo, 28)
    b = to_64bit_binary(new_seed_hi)
    
    return new_seed_lo, new_seed_hi

class Xoroshiro128PlusPlus:
    def __init__(self, seed_lo, seed_hi):
        self.seed_lo = seed_lo
        self.seed_hi = seed_hi

        if (self.seed_lo | self.seed_hi) == 0:
            self.seed_lo = -7046029254386353131
            self.seed_hi = 7640891576956012809
    def next_long(self):
        (l, l2) = self.seed_lo, self.seed_hi
        l3 = add_with_wrap_around(rotate_left(add_with_wrap_around(l, l2), 17), l)

        (self.seed_lo, self.seed_hi) = update_seeds(l, l2)
        
        return l3

class XoroshiroRandomSource:
    def __init__(self, seed_lo, seed_hi):
        self.random_number_generator = Xoroshiro128PlusPlus(seed_lo, seed_hi)

    def next_int(self):
        value = int(self.random_number_generator.next_long() & 0xFFFFFFFF)
        return value

    def next_int_in_range(self, bound):
        if bound <= 0:
            raise ValueError("Bound must be positive")
        
        l = self.next_int()
        l2 = l * bound
        l3 = l2 & 0xFFFFFFFF
        
        if l3 < bound:
            n2 = (0xFFFFFFFF + 1 - bound) % bound
            while l3 < n2:
                l = self.next_int()
                l2 = l * bound
                l3 = l2 & 0xFFFFFFFF
        
        result = l2 >> 32
        return result

    def fork_positional(self):
        new_seed_lo = self.random_number_generator.next_long()
        new_seed_hi = self.random_number_generator.next_long()
        return XoroshiroPositionalRandomFactory(new_seed_lo, new_seed_hi)
    
def from_bytes(byte_array):
    if len(byte_array) != 8:
        raise ValueError("Byte array must be 8 bytes long")

    value = struct.unpack('>Q', byte_array)[0]
    
    if value >= 2**63:
        value -= 2**64
    
    return value

class XoroshiroPositionalRandomFactory:
    def __init__(self, seed_lo, seed_hi):
        self.seed_lo = seed_lo
        self.seed_hi = seed_hi

    def from_hash_of(self, string):
        hash_bytes = hashlib.md5(string.encode('utf-8')).digest()
        seed_lo = from_bytes(hash_bytes[:8])
        seed_hi = from_bytes(hash_bytes[8:16])
        new_seed_lo = seed_lo ^ self.seed_lo
        new_seed_hi = seed_hi ^ self.seed_hi
        return XoroshiroRandomSource(new_seed_lo, new_seed_hi)

def solve_tool_target(inventory_seed, id_string):
    (seedlo, seedhi) = upgrade_seed_to_128bit(inventory_seed)

    positional_source = XoroshiroRandomSource(seedlo, seedhi).fork_positional().from_hash_of(id_string)
    result = 40 + positional_source.next_int_in_range(154 - 2 * 40)
    
    return result