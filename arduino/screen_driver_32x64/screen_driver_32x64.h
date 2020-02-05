/** @file  screen_driver_32x64.h
 *  @brief Contains definitions for the 32x64 LED Screen
 */

#define SCREEN_HEIGHT 32
#define SCREEN_WIDTH  64

typedef struct cursor_struct {
  int row;
  int col;
} cursor_t;

typedef struct screen_state_struct {
  uint16_t curr_color;
} screen_state_t;
