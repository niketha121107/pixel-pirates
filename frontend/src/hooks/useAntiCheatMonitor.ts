import { useEffect, useCallback, useRef, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';

interface ViolationWarning {
  violation_count: number;
  warning_number: number;
  message: string;
  is_suspended: boolean;
}

interface UseAntiCheatProps {
  testActive: boolean;
  onViolationWarning?: (warning: ViolationWarning) => void;
  onSuspension?: () => void;
}

export const useAntiCheatMonitor = ({ testActive, onViolationWarning, onSuspension }: UseAntiCheatProps) => {
  const { user, token } = useAuth();
  const [suspensionStatus, setSuspensionStatus] = useState<any>(null);
  const violationTimeoutRef = useRef<NodeJS.Timeout>();
  const screenRecordingRef = useRef<boolean>(false);

  // Prevent screenshots using multiple methods
  useEffect(() => {
    if (!testActive) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      // Print Screen, Snip & Sketch, etc.
      if (e.key === 'PrintScreen' || (e.ctrlKey && e.shiftKey && e.key === 's')) {
        e.preventDefault();
        recordViolation('screenshot');
        return false;
      }
    };

    const handleContextMenu = (e: MouseEvent) => {
      // Right-click menu (often used for screenshots)
      e.preventDefault();
      recordViolation('screenshot');
      return false;
    };

    const handleCopy = (e: ClipboardEvent) => {
      if (testActive) {
        e.preventDefault();
        recordViolation('copy_attempt');
      }
    };

    window.addEventListener('keydown', handleKeyDown, true);
    document.addEventListener('contextmenu', handleContextMenu, true);
    document.addEventListener('copy', handleCopy, true);

    // Disable screenshot via CSS
    document.documentElement.style.userSelect = 'none';
    document.documentElement.style.webkitUserSelect = 'none' as any;

    return () => {
      window.removeEventListener('keydown', handleKeyDown, true);
      document.removeEventListener('contextmenu', handleContextMenu, true);
      document.removeEventListener('copy', handleCopy, true);
      document.documentElement.style.userSelect = 'auto';
      document.documentElement.style.webkitUserSelect = 'auto' as any;
    };
  }, [testActive]);

  // Monitor tab switching
  useEffect(() => {
    if (!testActive) return;

    const handleVisibilityChange = () => {
      if (document.hidden) {
        // User switched away from tab
        recordViolation('tab_switch');
      }
    };

    const handleBlur = () => {
      // Window lost focus
      recordViolation('tab_switch');
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('blur', handleBlur);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('blur', handleBlur);
    };
  }, [testActive]);

  // Prevent fullscreen exit during test
  useEffect(() => {
    if (!testActive) return;

    const preventFullscreenExit = (e: any) => {
      if (document.fullscreenElement) {
        // Prevent exiting fullscreen
        e.preventDefault();
      }
    };

    document.addEventListener('fullscreenchange', preventFullscreenExit);

    return () => {
      document.removeEventListener('fullscreenchange', preventFullscreenExit);
    };
  }, [testActive]);

  // Record violation
  const recordViolation = useCallback(
    async (violationType: string) => {
      if (!token || !user) return;

      try {
        const response = await axios.post(
          `${import.meta.env.VITE_API_URL}/api/mock-test/record-violation`,
          { violation_type: violationType },
          {
            headers: {
              Authorization: `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          }
        );

        const warning: ViolationWarning = {
          violation_count: response.data.violation_count,
          warning_number: response.data.warning_number,
          message: response.data.message,
          is_suspended: response.data.is_suspended,
        };

        if (response.data.is_suspended) {
          setSuspensionStatus({
            suspended: true,
            until: response.data.suspension_until,
          });
          onSuspension?.();
        } else {
          onViolationWarning?.(warning);
        }
      } catch (error) {
        console.error('Error recording violation:', error);
      }
    },
    [token, user, onViolationWarning, onSuspension]
  );

  // Check suspension status on mount
  useEffect(() => {
    if (!token || !user) return;

    const checkSuspension = async () => {
      try {
        const response = await axios.get(
          `${import.meta.env.VITE_API_URL}/api/mock-test/suspension-status`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (response.data.is_suspended) {
          setSuspensionStatus({
            suspended: true,
            until: response.data.suspension_until,
          });
        } else if (response.data.suspension_lifted) {
          setSuspensionStatus(null);
        }
      } catch (error) {
        console.error('Error checking suspension status:', error);
      }
    };

    checkSuspension();
  }, [token, user]);

  return {
    suspensionStatus,
    recordViolation,
  };
};
